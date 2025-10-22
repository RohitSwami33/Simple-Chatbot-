# langgraph_tool_backend.py

import os
import sqlite3
import requests
from dotenv import load_dotenv

# LangGraph and LangChain Imports
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# Google Gemini Import
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file (for local development)
load_dotenv()

# -------------------
# 1. LLM Initialization with Error Handling
# -------------------
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set. Please configure it in Streamlit Secrets.")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0
    )
    print("--- LLM INITIALIZED SUCCESSFULLY ---")
except Exception as e:
    print(f"!!! CRITICAL ERROR: Could not initialize LLM. Reason: {e} !!!")
    raise

# -------------------
# 2. Tool Definitions
# -------------------
# Web Search Tool
search_tool = DuckDuckGoSearchRun(region="us-en")

# Calculator Tool
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

# Stock Price Tool
@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage. Requires an ALPHA_VANTAGE_API_KEY.
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return {"error": "ALPHA_VANTAGE_API_KEY not set. Please configure it in Streamlit Secrets."}
        
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    try:
        r = requests.get(url)
        r.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return r.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch stock price: {e}"}

# List of all tools available to the agent
tools = [search_tool, calculator, get_stock_price]

# Bind the tools to the LLM
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. State Definition
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Node Definitions
# -------------------
def agent_node(state: ChatState):
    """The main agent node that decides whether to use a tool or answer directly."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# The ToolNode is a pre-built node from LangGraph that executes tools
tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer (for persistent memory)
# -------------------
try:
    conn = sqlite3.connect("chatbot.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    print("--- SQLITE CHECKPOINTER INITIALIZED ---")
except Exception as e:
    print(f"!!! ERROR: Could not initialize SQLite checkpointer. Reason: {e} !!!")
    raise

# -------------------
# 6. Graph Compilation
# -------------------
graph = StateGraph(ChatState)

# Add nodes to the graph
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

# Define the entry point
graph.set_entry_point("agent")

# Add conditional edges from the agent node
# The `tools_condition` function checks if the LLM's last message has tool calls
graph.add_conditional_edges(
    "agent",
    tools_condition,
    # If tools are called, route to the "tools" node, otherwise end the conversation
    {"tools": "tools", END: END}
)

# Add an edge from the "tools" node back to the "agent" node
# This allows the agent to use the tool's output to generate a final answer
graph.add_edge("tools", "agent")

# Compile the graph with the checkpointer to enable memory
chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper Function
# -------------------
def retrieve_all_threads():
    """Helper function to get all conversation threads from the database."""
    all_threads = set()
    try:
        for checkpoint in checkpointer.list(None):
            if checkpoint.config and "configurable" in checkpoint.config:
                thread_id = checkpoint.config["configurable"].get("thread_id")
                if thread_id:
                    all_threads.add(thread_id)
    except Exception as e:
        print(f"!!! ERROR: Could not retrieve threads. Reason: {e} !!!")
    return list(all_threads)
