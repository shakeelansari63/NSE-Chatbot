import gradio as gr

from .navbar import navbar


def docs_page():
    with gr.Blocks():
        navbar()
        gr.Markdown(
            """
            # 🤖 NSE Chatbot
            ## ‎
            ## 🌟 Overview

            The **NSE Chatbot** is an AI-powered conversational agent designed to provide users with rapid and accurate information concerning the National Stock Exchange of India (NSE).
            The chatbot is backed by the **Model Context Protocol (MCP) Server**, which is the core data and processing engine, and is also directly accessible for advanced users.

            ## ‎
            ## ✨ Features

            ### The NSE Chatbot offers the following core capabilities:

            | Feature | Description | Key Capabilities | Example Query |
            | :--- | :--- | :--- | :--- |
            | **📈 Query Stock Prices** | Provides **real-time** stock quotes and key trading metrics for NSE-listed companies. | Retrieve **latest stock prices**, current trading price, high/low. | "What is the current price of **Reliance Industries**?" |
            | **📊 Query Stock History and Trend** | Accesses historical price data and performs automated trend analysis over specified timeframes. | Access **historical closing prices**, **analyze the trend** (upward/downward/volatile). | "Show me the price history and trend for **TCS** over the last 90 days." |
            | **🔍 Search Companies by Industry/Sector** | Allows users to filter and list companies based on their business classification. | **Categorized Search** by **Industry** (e.g., IT) or **Sector** (e.g., Energy). | "List top 10 companies in the **Automobile sector**." |
            | **💰 Analyze Company Financials** | Extracts and summarizes critical financial performance metrics from official corporate filings. | **Financial Data Extraction** of **Revenue**, **Net Profit**, **EPS**, etc., from reports. | "Summarize the **Net Profit** for **Maruti Suzuki**." |

            ---

            ## 💻 [MCP](https://modelcontextprotocol.io/docs/getting-started/intro) Server Direct Access

            The core engine powering the chatbot is the tools defined in **MCP Server**. This server provides a direct, programmatic interface for users who require more granular control over data retrieval and analysis, bypassing the conversational layer.

            ### ‎
            ### MCP Server: [http://nse-chatbot.azurewebsites.net/mcp](http://nse-chatbot.azurewebsites.net/mcp)
            ### ‎
            ### Sample Python code to access MCP server
            ### ‎
            ```python
            import asyncio
            from fastmcp.client import Client
            from fastmcp.client.transports import StreamableHTTPTransport

            async def main():
                # Define the URL of your remote streamable HTTP MCP server
                server_url = "http://nse-chatbot.azurewebsites.net/mcp"

                # Create a StreamableHTTPTransport instance
                transport = StreamableHTTPTransport(url=server_url)

                # Create an MCP client instance using the http transport
                client = Client(transport=transport)

                async with client:
                    try:
                        # Example: Ping the server to check connectivity
                        ping_result = await client.ping()
                        print(f"Server ping response: {ping_result}")

                        # Example: List available tools on the server
                        tools = await client.list_tools()
                        print(f"Available tools: {tools}")

                        # Example: Call a specific tool (replace 'your_tool_name' and arguments as needed)
                        if "search_nse_stocks_by_name_or_symbol" in tools:
                            stocks = await client.call_tool("search_nse_stocks_by_name_or_symbol", {"symbol": "Tata Motors"})
                            print(f"Found Stocks: {str(stocks)}")
                        else:
                            print("Tool 'greet' not found on the server.")

                    except Exception as e:
                        print(f"An error occurred: {e}")

            if __name__ == "__main__":
                asyncio.run(main())
            ```
            """
        )
