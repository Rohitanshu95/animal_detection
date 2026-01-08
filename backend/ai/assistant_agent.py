"""
LangGraph Assistant Agent
Conversational AI agent for wildlife incident analysis
"""

import json
from typing import Dict, List, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os


class WildlifeAssistant:
    """Conversational assistant for wildlife incident analysis"""

    def __init__(self, db_collection, vector_store_path="vector_store"):
        """
        Initialize assistant

        Args:
            db_collection: MongoDB collection
            vector_store_path: Path to vector store
        """
        self.db_collection = db_collection
        self.vector_store_path = vector_store_path

        # Initialize LLM
        api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.2
        )

        # Initialize tools
        self.tools = self._create_tools()

        # Create agent
        self.agent = self._create_agent()

    def _create_tools(self) -> List:
        """Create tools for the agent"""
        from langchain.tools import Tool
        from .tools.db_tools import DatabaseTools
        from .tools.vector_tools import VectorSearchTools

        # Database tools
        db_tools_instance = DatabaseTools(self.db_collection)

        # Vector search tools
        vector_tools_instance = VectorSearchTools(self.vector_store_path)

        tools = [
            # Database query tools
            Tool(
                name="search_incidents",
                description="Search wildlife incidents by keywords, location, animals, status, or date range. Input should be a dict with optional fields: query, location, animals, status, date_from, date_to, limit. Example: {'query': 'elephant', 'limit': 5}",
                func=lambda x: self._async_wrapper(
                    db_tools_instance.search_incidents, x),
            ),
            Tool(
                name="get_statistics",
                description="Get overall statistics about incidents including total count, breakdown by status, top animals, and top locations. No input required.",
                func=lambda x: self._async_wrapper(
                    db_tools_instance.get_statistics),
            ),
            Tool(
                name="get_trends",
                description="Calculate trends for a specific field over time. Input should be a dict with 'field' (e.g., 'animals', 'location') and optional 'period_days'. Example: {'field': 'animals', 'period_days': 30}",
                func=lambda x: self._async_wrapper(
                    db_tools_instance.calculate_trends, x),
            ),
            Tool(
                name="aggregate_data",
                description="Aggregate incidents by a specific field to see top values and counts. Input should be a dict with 'field' and optional 'limit'. Example: {'field': 'location', 'limit': 10}",
                func=lambda x: self._async_wrapper(
                    db_tools_instance.aggregate_by_field, x),
            ),

            # Vector search tools
            Tool(
                name="semantic_search",
                description="Perform semantic search to find incidents similar in meaning to a query. Better than keyword search for understanding context. Input should be the search query text.",
                func=lambda x: vector_tools_instance.semantic_search(
                    x, top_k=5),
            ),

            # Calculation tool
            Tool(
                name="calculate",
                description="Perform mathematical calculations. Input should be a Python expression as string. Example: '(100 + 50) * 2' or 'sum([10, 20, 30])'",
                func=lambda x: eval(x) if isinstance(x, str) else x,
            ),
        ]

        return tools

    def _async_wrapper(self, async_func, *args):
        """Wrapper to run async functions synchronously"""
        import asyncio
        loop = asyncio.get_event_loop()
        if len(args) == 0:
            return loop.run_until_complete(async_func())
        else:
            # Parse string to dict if needed
            arg = args[0]
            if isinstance(arg, str):
                try:
                    arg = eval(arg)
                except:
                    arg = {'query': arg}
            return loop.run_until_complete(async_func(**arg) if isinstance(arg, dict) else async_func(arg))

    def _create_agent(self):
        """Create the conversational agent"""

        # System prompt
        system_prompt = """You are an expert wildlife crime analyst assistant. You help users analyze wildlife smuggling incidents and patterns.

Your capabilities:
- Search and filter incident data
- Analyze trends and patterns
- Provide statistical insights
- Answer questions about specific incidents
- Identify correlations and anomalies

When answering:
1. Be clear and concise
2. Use data to support your answers
3. Suggest follow-up analysis when relevant
4. Explain your reasoning
5. If you use tools, explain what you found

Available tools:
- search_incidents: Search by keywords, location, animals, status, or dates
- get_statistics: Get overall statistics
- get_trends: Analyze trends over time
- aggregate_data: Group and count by field
- semantic_search: Find similar incidents by meaning
- calculate: Perform calculations

You have access to a database of wildlife smuggling incidents with information about animals, locations, dates, quantities, and more.

Be helpful, analytical, and professional.

Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

        # Create prompt template
        prompt = PromptTemplate.from_template(system_prompt)

        # Create agent
        agent = create_react_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=5,
            handle_parsing_errors=True
        )

        return agent_executor

    def chat(self, message: str, chat_history: List[Dict] = None) -> Dict:
        """
        Process a user message and return response

        Args:
            message: User message
            chat_history: Previous conversation history

        Returns:
            Response dict with message and metadata
        """
        # For now, we'll use the message directly without complex history handling
        # This avoids the typing issues

        try:
            # Run agent with simple input
            result = self.agent.invoke({"input": message})

            # Extract response
            response_text = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])

            # Format tool calls for transparency
            tool_calls = []
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step
                    tool_calls.append({
                        "tool": getattr(action, 'tool', 'unknown'),
                        "input": str(getattr(action, 'tool_input', '')),
                        # Truncate long outputs
                        "output": str(observation)[:500]
                    })

            return {
                "success": True,
                "message": response_text,
                "tool_calls": tool_calls,
                "has_tool_calls": len(tool_calls) > 0
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"I encountered an error: {str(e)}",
                "error": str(e),
                "tool_calls": []
            }

    async def chat_streaming(self, message: str, chat_history: List[Dict] = None):
        """
        Stream response (for future implementation)

        Args:
            message: User message
            chat_history: Previous conversation

        Yields:
            Response chunks
        """
        # For now, just yield the full response
        response = self.chat(message, chat_history)
        yield response


def create_assistant(db_collection, vector_store_path="vector_store"):
    """
    Factory function to create assistant

    Args:
        db_collection: MongoDB collection
        vector_store_path: Path to vector store

    Returns:
        WildlifeAssistant instance
    """
    return WildlifeAssistant(db_collection, vector_store_path)


# Convenience function for simple queries
async def ask_assistant(
    query: str,
    db_collection,
    chat_history: List[Dict] = None
) -> str:
    """
    Simple query interface

    Args:
        query: User question
        db_collection: MongoDB collection
        chat_history: Optional chat history

    Returns:
        Response text
    """
    assistant = create_assistant(db_collection)
    result = assistant.chat(query, chat_history)
    return result.get("message", "")
