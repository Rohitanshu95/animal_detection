"""
Simplified AI Assistant for Wildlife Incident Analysis
Direct LLM integration without complex LangGraph setup
"""

import os
from typing import Dict, List, Any
from .llm import generate_text, generate_text_with_json

class WildlifeAssistant:
    """Simplified conversational assistant for wildlife incident analysis"""

    def __init__(self, db_collection, vector_store_path="vector_store"):
        """
        Initialize assistant

        Args:
            db_collection: MongoDB collection
            vector_store_path: Path to vector store
        """
        self.db_collection = db_collection
        self.vector_store_path = vector_store_path

    async def chat(self, message: str, chat_history: List[Dict] = None, thread_id: str = "default_thread") -> Dict:
        """
        Process a user message and generate a response

        Args:
            message: User message
            chat_history: Previous conversation history
            thread_id: ID to track conversation state

        Returns:
            Response dict with message and metadata
        """
        try:
            # Build context from chat history
            context = ""
            if chat_history:
                context = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in chat_history[-5:]])  # Last 5 messages
                context = f"Previous conversation:\n{context}\n\n"

            # Check if user is asking for charts/graphs
            chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'show me', 'display']
            is_chart_request = any(keyword in message.lower() for keyword in chart_keywords)

            if is_chart_request:
                # Generate chart data
                chart_prompt = f"""{context}You are a data visualization assistant for wildlife incident analysis.

User requested a chart/graph: {message}

Generate chart data in JSON format with the following structure:
{{
    "chart_type": "bar|line|pie|doughnut",
    "title": "Chart Title",
    "data": {{
        "labels": ["Label1", "Label2", "Label3"],
        "datasets": [{{
            "label": "Dataset Label",
            "data": [10, 20, 30],
            "backgroundColor": ["#color1", "#color2", "#color3"]
        }}]
    }},
    "description": "Brief description of what this chart shows"
}}

Make the chart relevant to wildlife incidents. Use realistic sample data if specific data isn't available."""

                chart_json = await generate_text_with_json(chart_prompt, temperature=0.2)
                import json
                try:
                    chart_data = json.loads(chart_json)
                    response_text = f"I've generated a chart for you: {chart_data.get('description', 'Chart visualization')}"

                    return {
                        "success": True,
                        "message": response_text,
                        "chart_data": chart_data,
                        "tool_calls": [],
                        "has_tool_calls": False
                    }
                except json.JSONDecodeError:
                    response_text = "I tried to generate a chart but encountered an issue with the data format. Let me provide a text-based response instead."
            else:
                # Regular text response
                prompt = f"""{context}You are a helpful AI assistant specialized in wildlife smuggling and incident analysis.

Current user question: {message}

Please provide a helpful, accurate response. If the user is asking about wildlife incidents, offer to search the database or provide statistics. Keep your response concise but informative."""

                response_text = await generate_text(prompt, temperature=0.3, max_tokens=1000)

            return {
                "success": True,
                "message": response_text,
                "tool_calls": [],
                "has_tool_calls": False
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
