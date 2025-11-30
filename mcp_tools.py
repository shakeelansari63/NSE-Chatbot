from datetime import date, datetime
from typing import Any

from fastmcp import FastMCP

from dbman.helper import (
    get_companies_in_specified_industry,
    search_nse_company_by_name_or_symbol_indb,
    search_sector_or_industry_indb,
)
from nse.helper import (
    get_capital_market_state,
    get_stock_corporate_filing_info,
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
    """Provides the current date and time in the format DD-MM-YYYY HH:MM:SS"""
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


# Register MCP
@mcp.tool()
async def check_equity_market_status() -> str:
    """Check whether the Equity / Capital Market is open or closed. Returns a string indicating the market status."""
    market_state = get_capital_market_state()

    if market_state is None:
        return "UNKNOWN: Unable to get Market Status from NSE"

    return str(market_state)


@mcp.tool()
def get_current_stock_price(symbol: str) -> dict[str, Any]:
    """
    Returns the Current price and previous day close price of the given stock symbol.
    If market is closed, CurrentPrice will be the Closing price on market day.

    :PARAMETERS:
        symbol: Stock Symbol

    :RESPONSE:
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
def get_stock_history_prices_for_range_not_more_than_1_year(
    symbol: str,
    from_date: str,
    to_date: str,
) -> dict[str, Any] | str:
    """
    Returns the historical prices of a stock for selected date range. Make sure the range is not more than 1 year.
    This tool does not support giving data for range more than 1 year.

    :PARAMETERS:
        symbol: Stock Symbol
        from_date: Range Start Date in DD-MM-YYYY format.
        to_date: Range End Date in DD-MM-YYYY format.

    :RESPONSE:
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
def get_stock_running_at_52week_high() -> list[dict[str, str]] | str:
    """Returns the list of stock that are currently running at their 52-week high price.

    Example Output: [
            {"TCS" : "Tata Consultancy Services Limited"},
            {"INFY" : "Infosys Limited"}
        ]
    """
    data: list[Stock52weekAnalysis] | None = get_stock_running_52week_high()
    if data is None:
        return "Unable to fetch 52-week high data from NSE"

    return [{item.symbol: item.comapnyName} for item in data]


@mcp.tool()
def get_stock_running_at_52week_low() -> list[dict[str, str]] | str:
    """Returns the list of stocks that are currently running at their 52-week low price.

    Example Output: [
            {"TCS" : "Tata Consultancy Services Limited"},
            {"INFY" : "Infosys Limited"}
        ]
    """
    data: list[Stock52weekAnalysis] | None = get_stock_running_52week_low()
    if data is None:
        return "Unable to fetch 52-week low data from NSE"

    return [{item.symbol: item.comapnyName} for item in data]


@mcp.tool()
def weekly_volume_gainer_stocks() -> list[dict[str, str]] | str:
    """Returns the list of stocks which are weekly volume gainers.

    Example Output: [
            {"TCS" : "Tata Consultancy Services Limited"},
            {"INFY" : "Infosys Limited"}
        ]
    """
    data: list[StockWeeklyVolumeGainers] | None = get_weekly_volume_gainers()
    if data is None:
        return "Unable to fetch weekly volume gainers from NSE"

    return [{item.symbol: item.companyName} for item in data]


@mcp.tool()
def search_nse_stocks_by_name_or_symbol(
    search_key: str,
) -> list[dict[str, str]] | str:
    """
    Search the NSE Database for companies whose name or symbol matches the search key and returns a complete list.
    The search key will be searched in Company name or Symbol and nowhere else.

    :PARAMETERS:
        search_key: The key to search for in the NSE companies list.

    Example Output: [
            {"TCS" : "Tata Consultancy Services Limited"},
            {"INFY" : "Infosys Limited"}
        ]
    """
    companies = search_nse_company_by_name_or_symbol_indb(search_key)

    return [{company.symbol: company.name} for company in companies]


@mcp.tool()
def search_nse_sector_or_industry_keys(search_key: str) -> list[str]:
    """Returns a list of NSE registered Industries keys which match the search key.
    These keys can be used to search companies in specific industry.

    Example Input: "IT"
    Example Output: ["IT - Hardware", "Information Technology"]
    """
    return search_sector_or_industry_indb(search_key)


@mcp.tool()
def get_top_stocks_in_industries_by_industry_keys(
    industry_keys: list[str],
    top_n: int | None = 10,
) -> list[dict[str, str]]:
    """
    Search the NSE database for list of companies which operate in provided industry and returns list of top n stocks by market cap.
    !IMPORTANT: The Industry key should match exactly with that in database.
    Use the other provided tool to search keys for industries registered in NSE Database first.

    :PARAMETERS:
        sectors_or_industries: List of sectors or industries to search the company.
        top_n: Optional integer parameter to specify the top number of companies to return. Defaults to 10 if not provided.

    Example Input: ["Information Technology"]
    Example Output: [
            {"TCS" : "Tata Consultancy Services Limited"},
            {"INFY" : "Infosys Limited"}
        ]
    """
    if top_n is None:
        top_n = 10

    return get_companies_in_specified_industry(industry_keys, top_n)


@mcp.tool()
def analyse_stock_corporate_filings_financial_results_corporate_actions(
    symbol: str,
) -> dict[str, Any]:
    """Returns a dictionary containing last board meeting detail, latest financial results,
    corporate actions like dividend, last few announcements and Shareholding pattern for a given stock symbol.

    :PARAMETERS:
        symbol: The stock symbol to search for.

    Example Input: "TCS"
    Example Output: {
        "Latest Board Meeting": "<Details of latest board meeting>",
        "Latest Financial Results": "<Latest Financial Results>",
        "Latest Corporate Actions": "<Corporate Actions like dividend etc>",
        "Latest Shareholding Pattern": <Current Shareholding Pattern like percent share held by public / employees>,
    }
    """
    detail = get_stock_corporate_filing_info(symbol)

    if detail is None:
        return {"Error": f"Corporate filings not found for {symbol}"}

    # Latest Board Meeting annnouncement
    latest_board_meeting = (
        detail.borad_meeting.data[0] if len(detail.borad_meeting.data) > 0 else None
    )

    latest_board_meeting_details = (
        f"{latest_board_meeting.meetingdate}: {latest_board_meeting.purpose}"
        if latest_board_meeting
        else "No Information Available"
    )

    # Latest Financial Results
    latest_financial_results = (
        detail.financial_results.data[0]
        if len(detail.financial_results.data) > 0
        else None
    )

    latest_financial_results_details = (
        f"from: {latest_financial_results.from_date if latest_financial_results.from_date else 'NA'}, "
        + f"to: {latest_financial_results.to_date if latest_financial_results.to_date else 'NA'}, "
        + f"income (₹ Crores): {latest_financial_results.income if latest_financial_results.income else 'NA'}, "
        + f"earning per share (₹): {latest_financial_results.reDilEPS if latest_financial_results.reDilEPS else 'NA'}, "
        + f"profit / loss before tax (₹ Crores): {latest_financial_results.reProLossBefTax if latest_financial_results.reProLossBefTax else 'NA'}, "
        + f"net profit / loss (₹ Crores): {latest_financial_results.proLossAftTax if latest_financial_results.proLossAftTax else 'NA'}"
        if latest_financial_results
        else "No Information Available"
    )

    # Take Top 5 Corporate Actions
    latest_corporate_actions = (
        detail.corporate_actions.data[:5]
        if len(detail.corporate_actions.data) > 5
        else detail.corporate_actions.data
    )

    latest_corporate_actions_details = (
        ", ".join(
            [
                f"{action.exdate}: {action.purpose}"
                for action in latest_corporate_actions
            ]
        )
        if latest_corporate_actions
        else "No Information Available"
    )

    # Take latest Shareholding Pattern
    latest_shareholding_pattern_date, latest_shareholding_pattern = max(
        detail.shareholdings_patterns.data.items(),
        key=lambda x: datetime.strptime(x[0], "%d-%b-%Y"),
    )

    latest_shareholding_pattern_details = (
        f"date: {latest_shareholding_pattern_date if latest_shareholding_pattern_date else 'NA'}, "
        + ", ".join(
            [
                f"{list(shareholder.items())[0][0]}: {list(shareholder.items())[0][1]}%"
                for shareholder in latest_shareholding_pattern
                if len(list(shareholder.items())) > 0
            ]
        )
        if latest_shareholding_pattern
        else "No Information Available"
    )

    # Return Final Detail
    return {
        "Latest Board Meeting": latest_board_meeting_details,
        "Financial Results": latest_financial_results_details,
        "Corporate Actions": latest_corporate_actions_details,
        "Shareholding Pattern": latest_shareholding_pattern_details,
    }
