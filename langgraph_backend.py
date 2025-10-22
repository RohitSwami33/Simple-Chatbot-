

import os
import sqlite3
from dotenv import load_dotenv

# LangGraph and LangChain Imports
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages

# Google Gemini Import
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # This will raise an error if the key is not found, which is good for debugging.
        raise ValueError("GOOGLE_API_KEY environment variable not set. Please configure it.")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0
    )
    print("--- LLM INITIALIZED SUCCESSFULLY ---")
except Exception as e:
    print(f"!!! CRITICAL ERROR: Could not initialize LLM. Reason: {e} !!!")
    # Exit the script so the import fails predictably and the error is visible in logs.
    raise

# -------------------
# 2. State Definition
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 3. Node Definition
# -------------------
def chat_node(state: ChatState):
    """The main chat node that calls the LLM with the conversation history."""
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}


try:
    conn = sqlite3.connect("chatbot.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    print("--- SQLITE CHECKPOINTER INITIALIZED ---")
except Exception as e:
    print(f"!!! ERROR: Could not initialize SQLite checkpointer. Reason: {e} !!!")
    raise


graph = StateGraph(ChatState)

# Add the single chat node to the graph
graph.add_node("chat_node", chat_node)

# Define the workflow: Start -> chat_node -> End
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# Compile the graph with the checkpointer to enable memory
chatbot = graph.compile(checkpointer=checkpointer)



def retrieve_all_threads():
    """Helper function to get all conversation threads from the database."""
    all_threads = set()
    try:
        for checkpoint in checkpointer.list(None):
            # Ensure the config and thread_id exist before accessing
            if checkpoint.config and "configurable" in checkpoint.config:
                thread_id = checkpoint.config["configurable"].get("thread_id")
                if thread_id:
                    all_threads.add(thread_id)
    except Exception as e:
        print(f"!!! ERROR: Could not retrieve threads. Reason: {e} !!!")
    return list(all_threads)

