
# LangGraph Chatbot

A powerful conversational AI chatbot built with LangGraph, LangChain, and Google's Gemini AI model. Features persistent conversation memory, multi-threading support, and integrated tools for web search, calculations, and stock price retrieval.

## Features

- **Persistent Memory**: Conversations are saved using SQLite checkpointing, allowing you to resume chats across sessions
- **Multi-Threading**: Manage multiple conversation threads simultaneously with easy thread switching
- **Streaming Responses**: Real-time token streaming for a smooth chat experience
- **Tool Integration**: 
  - 🔍 Web search using DuckDuckGo
  - 🧮 Calculator for arithmetic operations
  - 📈 Stock price lookup via Alpha Vantage API
- **Modern UI**: Clean Streamlit interface with sidebar navigation
- **Google Gemini Integration**: Powered by Google's latest Gemini 2.0 Flash model

## Project Structure

```
Simple-Chatbot/
├── data/
│   ├── gemini_info.txt
│   └── langgraph_info.txt
├── langgraph_backend.py              # Basic chatbot backend
├── langgraph_database_backend.py     # Backend with database persistence
├── langgraph_tool_backend.py         # Backend with tool integration
├── streamlit_frontend.py             # Basic frontend
├── streamlit_frontend_streaming.py   # Frontend with streaming
├── streamlit_frontend_database.py    # Frontend with thread management
├── streamlit_frontend_threading.py   # Advanced threading frontend
├── streamlit_frontend_tool.py        # Full-featured frontend with tools
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- Google API Key (for Gemini AI)
- Alpha Vantage API Key (optional, for stock price feature)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Simple-Chatbot.git
   cd Simple-Chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here  # Optional
   ```

   To get your API keys:
   - **Google API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Alpha Vantage Key**: Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)

## Usage

### Basic Chatbot
Run the simple version without tools:
```bash
streamlit run streamlit_frontend.py
```

### Chatbot with Streaming
Experience real-time response streaming:
```bash
streamlit run streamlit_frontend_streaming.py
```

### Chatbot with Thread Management
Manage multiple conversations with persistent storage:
```bash
streamlit run streamlit_frontend_database.py
```

### Full-Featured Chatbot (Recommended)
Launch the complete version with all tools and features:
```bash
streamlit run streamlit_frontend_tool.py
```

## Available Tools

### 1. Web Search
Search the web for current information using DuckDuckGo.

**Example**: "Search for the latest news about AI"

### 2. Calculator
Perform basic arithmetic operations (add, sub, mul, div).

**Example**: "Calculate 245 multiplied by 67"

### 3. Stock Price Lookup
Get real-time stock prices for any symbol.

**Example**: "What's the current price of AAPL stock?"

## How It Works

The chatbot uses LangGraph to create a stateful conversation flow:

1. **Agent Node**: Analyzes user input and decides whether to use tools or respond directly
2. **Tool Node**: Executes requested tools (search, calculator, stock lookup)
3. **Checkpointer**: Saves conversation state to SQLite database
4. **State Graph**: Manages the flow between nodes with conditional edges

```
User Input → Agent → Tool (if needed) → Agent → Response
                ↓                          ↑
            Checkpointer (Memory)
```

## Configuration

### Model Settings
The chatbot uses `gemini-2.0-flash-exp` by default. You can modify this in the backend files:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",  # Change model here
    temperature=0  # Adjust temperature (0-1)
)
```

### Thread Management
Conversations are stored with unique thread IDs. The database file `chatbot.db` is created automatically on first run.

## Development

### Adding New Tools

To add a custom tool, edit `langgraph_tool_backend.py`:

```python
from langchain_core.tools import tool

@tool
def your_custom_tool(param: str) -> dict:
    """
    Description of what your tool does.
    """
    # Your implementation
    return {"result": "your result"}

# Add to tools list
tools = [search_tool, calculator, get_stock_price, your_custom_tool]
```

### Customizing the UI

Modify the Streamlit frontend files to customize the appearance and behavior of the chatbot interface.

## Troubleshooting

### Common Issues

**Error: GOOGLE_API_KEY not set**
- Ensure your `.env` file exists and contains a valid Google API key
- Restart the application after creating/modifying the `.env` file

**Error: Could not initialize SQLite checkpointer**
- Check file permissions in the project directory
- Delete `chatbot.db` and restart the application

**Tool not working**
- Verify the ALPHA_VANTAGE_API_KEY is set for stock price lookups
- Check your internet connection for web search functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)
- UI created with [Streamlit](https://streamlit.io/)

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This chatbot is for educational and development purposes. Ensure you comply with all API terms of service and rate limits.
