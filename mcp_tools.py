from fastmcp import FastMCP

from dbman.helper import (
    get_companies_in_sectors_or_industries,
    get_unique_sectors_and_industries,
    search_nse_company_indb,
)
from nse.helper import (
    get_all_market_pre_open,
    get_market_state,
    get_stock_details,
    get_stock_running_52week_high,
    get_stock_running_52week_low,
    get_weekly_volume_gainers,
)
from nse.models import (
    MarketPreOpenMcp,
    MarketStatusMcp,
    Stock52weekAnalysis,
    StockDetailResponse,
    StockWeeklyVolumeGainers,
)

mcp = FastMCP()


# Register MCP
@mcp.tool()
async def check_equity_market_status() -> str:
    """
    Check whether the Equity / Capital Market is up or not. Returns a string indicating the market status.
    :resp
        Market Status: OPEN / CLOSED
    """
    market_state: list[MarketStatusMcp] | None = get_market_state()

    if market_state is None:
        return "Unable to fetch Market Status from NSE"

    equity_market_state = list(
        filter(lambda x: x.market == "Capital Market", market_state)
    )[0]
    return equity_market_state.marketStatus


@mcp.tool()
def get_stock_closing_price(symbol: str) -> str:
    """
    Returns the closing price of the given stock symbol.

    :params
        symbol: Symbol / Code of Stock whose closing price is requested

    :resp
        Closing price of the stock from Market.
    """
    preopen_data: list[MarketPreOpenMcp] | None = get_all_market_pre_open()

    if preopen_data is None:
        return "Unable to fetch Symbols from NSE"

    price = None

    for d in preopen_data:
        if d.symbol == symbol:
            price = d.previousClose

    if price is None:
        return f"Symbol {symbol} not found in NSE Pre-Open Market Data"

    return f"Closing Price of {symbol} is INR {price}"


@mcp.tool()
def get_live_stock_price(symbol: str) -> str:
    """
    Returns the current live price of Stock registered in NSE.

    :params
        symbol: Symbol / Code of Stock whose price is requested

    :resp
        Current stock price from Market.
    """
    stock_detail: StockDetailResponse | None = get_stock_details(symbol)

    if stock_detail is None:
        return "Unable to fetch Stock Data from NSE"

    return f"Current Price of {symbol} is INR {stock_detail.priceInfo.lastPrice}"


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
