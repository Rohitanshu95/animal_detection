"""
LangGraph Assistant Agent
Conversational AI agent for wildlife incident analysis - Async Implementation
"""

import os
from typing import Dict, List, Any, TypedDict, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[list[BaseMessage], add_messages]

class WildlifeAssistant:
    """Conversational assistant for wildlife incident analysis using LangGraph (Async)"""

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
        if not api_key:
             print("Warning: GOOGLE_API_KEY not found. Agent may not function correctly.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.2
        )

        # Initialize tools
        self.tools = self._create_tools()
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Create graph
        self.graph = self._create_graph()

    def _create_tools(self) -> List:
        """Create tools for the agent"""
        from .tools.db_tools import create_langchain_tools
        from .tools.vector_tools import create_vector_tools

        # Database tools
        db_tools = create_langchain_tools(self.db_collection)

        # Vector search tools
        vector_tools = create_vector_tools(self.vector_store_path)

        # Combine tools
        return db_tools + vector_tools

    def _create_graph(self):
        """Create the LangGraph workflow"""
        
        # Define the chatbot node
        async def chatbot(state: AgentState):
            return {"messages": [await self.llm_with_tools.ainvoke(state["messages"])]}

        # Build graph
        builder = StateGraph(AgentState)
        
        # Add nodes
        builder.add_node("chatbot", chatbot)
        builder.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        builder.add_edge(START, "chatbot")
        builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        builder.add_edge("tools", "chatbot")
        
        # Compile graph with checkpointer
        memory = MemorySaver()
        return builder.compile(checkpointer=memory)

    async def chat(self, message: str, chat_history: List[Dict] = None, thread_id: str = "default_thread") -> Dict:
        """
        Process a user message asynchronously

        Args:
            message: User message
            chat_history: Previous conversation history
            thread_id: ID to track conversation state
            
        Returns:
            Response dict with message and metadata
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            input_message = HumanMessage(content=message)
            
            # Use ainvoke for async execution
            final_state = await self.graph.ainvoke({"messages": [input_message]}, config=config)
            
            messages = final_state["messages"]
            last_message = messages[-1]
            
            response_text = last_message.content
            
            # Extract tool calls from history for transparency
            tool_calls = []
            for msg in messages:
                if isinstance(msg, AIMessage) and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_calls.append({
                            "tool": tc.get("name"),
                            "input": str(tc.get("args")),
                            "output": "Executed" 
                        })

            return {
                "success": True,
                "message": response_text,
                "tool_calls": tool_calls,
                "has_tool_calls": len(tool_calls) > 0
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"I encountered an error: {str(e)}",
                "error": str(e),
                "tool_calls": []
            }

def create_assistant(db_collection, vector_store_path="vector_store"):
    """Factory function to create assistant"""
    return WildlifeAssistant(db_collection, vector_store_path)

async def ask_assistant(query: str, db_collection, chat_history: List[Dict] = None) -> str:
    """Simple query interface"""
    assistant = create_assistant(db_collection)
    result = await assistant.chat(query, chat_history)
    return result.get("message", "")
