BASE_URL = "https://www.nseindia.com"
EQUITY_URL = f"{BASE_URL}/get-quotes/equity?symbol="
MARKET_STATUS_URL = f"{BASE_URL}/api/marketStatus"
STOCK_QUOTE_URL = f"{BASE_URL}/api/quote-equity"
MARKET_PRE_OPEN_URL = f"{BASE_URL}/api/market-data-pre-open?key=ALL"
STOCKS_52_HIGH = f"{BASE_URL}/api/live-analysis-data-52weekhighstock"
STOCKS_52_LOW = f"{BASE_URL}/api/live-analysis-data-52weeklowstock"
WEEKLY_VOLUME_GAINERS = f"{BASE_URL}/api/live-analysis-volume-gainers"
NSE_COMPANIES_WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_National_Stock_Exchange_of_India"
NSE_COMPANIES_LIST_REDIFF_URL = "https://money.rediff.com/companies/nseall/"

NSE_HEADER: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    "Accept": "*/*",
    "Origin": BASE_URL,
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive",
}
