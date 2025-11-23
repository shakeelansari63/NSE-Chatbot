from datetime import datetime
from typing import Any

from fastmcp import FastMCP

from dbman.helper import (
    get_companies_in_sectors_or_industries,
    get_unique_sectors_and_industries,
    search_nse_company_indb,
)
from nse.helper import (
    get_capital_market_state,
    get_stock_details,
    get_stock_history_for_specific_range,
    get_stock_running_52week_high,
    get_stock_running_52week_low,
    get_weekly_volume_gainers,
)
from nse.models import (
    MarketStatus,
    Stock52weekAnalysis,
    StockDetailResponse,
    StockWeeklyVolumeGainers,
)

mcp = FastMCP()


# MCP Tool to Provide Current Date Time
@mcp.tool()
async def get_current_date_time() -> str:
    """
    Provides the current date and time in the format DD-MM-YYYY HH:MM:SS.

    :resp
        Current Date and Time: DD-MM-YYYY HH:MM:SS
    """
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


# Register MCP
@mcp.tool()
async def check_equity_market_status() -> str:
    """
    Check whether the Equity / Capital Market is open or closed. Returns a string indicating the market status.
    :resp
        Market Status: OPEN / CLOSED / UNKNOWN
    """
    market_state = get_capital_market_state()

    if market_state is None:
        return "UNKNOWN: Unable to get Market Status from NSE"

    return str(market_state)


@mcp.tool()
def get_current_stock_price(symbol: str) -> dict[str, Any]:
    """
    Returns the Current price and previous day close price of the given stock symbol.
    If market is closed, CurrentPrice will be the Closing price on market day.

    :params
        symbol: Symbol / Code of stock

    :resp
        {
            "Symbol": <Stock Symbol>,
            "CurrentPrice": <Current or Closing Price>,
            "PreviousClosePrice": <Closing Price on previous market day>,
        }
    """
    stock_detail: StockDetailResponse | None = get_stock_details(symbol)
    market_state = get_capital_market_state()

    if stock_detail is None or market_state is None:
        return {
            "Symbol": symbol,
            "CurrentPrice": stock_detail.priceInfo.lastPrice
            if stock_detail
            else "UNKNOWN",
            "PreviousClosePrice": stock_detail.priceInfo.previousClose
            if stock_detail
            else "UNKNOWN",
        }

    # Check for market status
    if market_state == MarketStatus.CLOSED or market_state == MarketStatus.CLOSE:
        return {
            "Symbol": symbol,
            "CurrentPrice": stock_detail.priceInfo.close,
            "PreviousClosePrice": stock_detail.priceInfo.previousClose,
        }

    return {
        "Symbol": symbol,
        "CurrentPrice": stock_detail.priceInfo.lastPrice,
        "PreviousClosePrice": stock_detail.priceInfo.previousClose,
    }


@mcp.tool()
def get_stock_history_prices(
    symbol: str,
    from_date: str,
    to_date: str,
) -> dict[str, Any] | str:
    """
    Returns the historical prices of a stock.

    :params
        symbol: The symbol of the stock.
        from_date: Start Date for Historical Data in DD-MM-YYYY format.
        to_date: End Date for Historical Data in DD-MM-YYYY format.

    :resp
        {<Symbol>:[
            {
                "date": <Date in YYYY-MM-DD Format>,
                "close": <Closing Price>,
            }, ...
        ],
        "highest": <Highest Price in Date Range>,
        "lowest": <Lowest Price in Date Range>}

    Example Input: symbol="IRCTC", from_date="01-01-2023", to_date="02-01-2023"
    Example Output: {"IRCTC":[
            {"date": "2023-01-01","open": 100.0,"close": 105.0,"high": 110.0,"low": 95.0},
            {"date": "2023-01-02","open": 105.0,"close": 110.0,"high": 115.0,"low": 100.0}
        ], "highest": 120.9, "lowest": 92.0}
    """
    data = get_stock_history_for_specific_range(symbol, from_date, to_date)

    if data is None:
        return "Unable to fetch historical data from NSE"

    stock_data = [
        {
            "date": stock.CH_TIMESTAMP,
            "close": stock.CH_OPENING_PRICE,
        }
        for stock in data
    ]

    return {
        symbol: stock_data,
        "highest": max(data, key=lambda x: x.CH_TRADE_HIGH_PRICE).CH_TRADE_HIGH_PRICE,
        "lowest": min(data, key=lambda x: x.CH_TRADE_LOW_PRICE).CH_TRADE_LOW_PRICE,
    }


@mcp.tool()
def get_stock_running_at_52week_high() -> list[str] | str:
    """
    Returns the list of stock symbols that are currently running at their 52-week high.

    :resp
        List of stock symbols running at 52-week high.
    """
    data: list[Stock52weekAnalysis] | None = get_stock_running_52week_high()
    if data is None:
        return "Unable to fetch 52-week high data from NSE"

    return [item.symbol for item in data]


@mcp.tool()
def get_stock_running_at_52week_low() -> list[str] | str:
    """
    Returns the list of stock symbols that are currently running at their 52-week low.

    :resp
        List of stock symbols running at 52-week low.
    """
    data: list[Stock52weekAnalysis] | None = get_stock_running_52week_low()
    if data is None:
        return "Unable to fetch 52-week low data from NSE"

    return [item.symbol for item in data]


@mcp.tool()
def weekly_volume_gainer_stocks() -> list[str] | str:
    """
    Returns the list of stock symbols that are weekly volume gainers.

    :resp
        List of stock symbols that are weekly volume gainers.
    """
    data: list[StockWeeklyVolumeGainers] | None = get_weekly_volume_gainers()
    if data is None:
        return "Unable to fetch weekly volume gainers from NSE"

    return [item.symbol for item in data]


@mcp.tool()
def search_nse_companies(search_key: str) -> list[dict[str, str]] | str:
    """
    Search the NSE Database for companies whose name or symbol matches the search key and returns a complete list.
    The search key will be searched in Company name or Symbol and nowhere else.

    :params
        search_key: The key to search for in the NSE companies list.

    :resp
        A list containing mapping object/dictionary where key is company symbol and value is company name.

    Example Output:
        [
            {"TCS" : "Tata Consultancy Services Limited"},
            {"INFY" : "Infosys Limited"}
        ]
    """
    companies = search_nse_company_indb(search_key)

    return [{company.symbol: company.name} for company in companies]


@mcp.tool()
def available_sectors_and_industries() -> list[str]:
    """
    Returns a complete list of Sectors or Industries against which companies are registered.

    :resp
        A list of sectors/industries.

    Example Output:
        ["IT - Hardware", "Commercial Goods"]
    """
    return get_unique_sectors_and_industries()


@mcp.tool()
def companies_in_sectors_and_industries(
    sectors_or_industries: list[str],
) -> list[dict[str, str]]:
    """
    Search the NSE database for list of companies which operate in provided sector or industry and returns complete list of companies with their symbols.
    The Sector or Industry name should match exactly with that in database.
    Use other tool provided to give complete list of sectors or industries registered in NSE Database first.

    :params
        sectors_or_industries: List of sectors or industries to search the company.

    :resp
        A list containing mapping object/dictionary where key is company symbol and value is company name.

    Example Input: ["Information Technology"]
    Example Output:
        [
            {"TCS" : "Tata Consultancy Services Limited"},
            {"INFY" : "Infosys Limited"}
        ]
    """
    return get_companies_in_sectors_or_industries(sectors_or_industries)
