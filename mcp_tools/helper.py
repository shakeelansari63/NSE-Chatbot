import re
from functools import cache

import httpx
from bs4 import BeautifulSoup

from . import config as conf
from .models import (
    MarketPreOpenApiResponse,
    MarketPreOpenMcp,
    MarketStatusApiResp,
    MarketStatusMcp,
    NSECompaniesList,
    Stock52weekAnalysis,
    Stock52WeekHighResponse,
    Stock52WeekLowResponse,
    StockDetailResponse,
    StockWeeklyVolumeGainerResponse,
    StockWeeklyVolumeGainers,
)
from .nse_http import NSEHttpClient


@cache
def _get_nse_client() -> NSEHttpClient:
    nse_client = NSEHttpClient()
    return nse_client


def _get_url_soup(url: str) -> BeautifulSoup | None:
    client = httpx.Client()
    response = client.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch URL: {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def get_market_state() -> list[MarketStatusMcp] | None:
    data = _get_nse_client().get_nse_data(conf.MARKET_STATUS_URL)
    if data is None:
        return None

    market_state = MarketStatusApiResp.model_validate(data)

    resp_market_state = [
        MarketStatusMcp(
            market=status.market,
            marketStatus=status.marketStatus,
            tradeDate=status.tradeDate,
            marketStatusMessage=status.marketStatusMessage,
        )
        for status in market_state.marketState
    ]

    return resp_market_state


def get_all_market_pre_open() -> list[MarketPreOpenMcp] | None:
    data = _get_nse_client().get_nse_data(conf.MARKET_PRE_OPEN_URL)
    if data is None:
        return None

    market_data = MarketPreOpenApiResponse.model_validate(data)
    return [
        MarketPreOpenMcp.model_validate(d.metadata.model_dump())
        for d in market_data.data
    ]


def get_stock_details(symbol: str) -> StockDetailResponse | None:
    data = _get_nse_client().get_nse_data(conf.STOCK_QUOTE_URL, {"symbol": symbol})

    if data is None:
        return None

    stock_data = StockDetailResponse.model_validate(data)
    return stock_data


def get_stock_running_52week_high() -> list[Stock52weekAnalysis] | None:
    data: Stock52WeekHighResponse = _get_nse_client().get_nse_data(conf.STOCKS_52_HIGH)
    if data is None:
        return None
    data: Stock52WeekHighResponse = Stock52WeekHighResponse.model_validate(data)
    return data.data


def get_stock_running_52week_low() -> list[Stock52weekAnalysis] | None:
    data = _get_nse_client().get_nse_data(conf.STOCKS_52_LOW)
    if data is None:
        return None
    data: Stock52WeekLowResponse = Stock52WeekLowResponse.model_validate(data)
    return data.data


def get_weekly_volume_gainers() -> list[StockWeeklyVolumeGainers] | None:
    data = _get_nse_client().get_nse_data(conf.WEEKLY_VOLUME_GAINERS)
    if data is None:
        return None
    data: StockWeeklyVolumeGainerResponse = (
        StockWeeklyVolumeGainerResponse.model_validate(data)
    )
    return data.data


def get_nse_company_list_from_rediff() -> list[NSECompaniesList] | None:
    soup = _get_url_soup(conf.NSE_COMPANIES_LIST_REDIFF_URL)
    if soup is None:
        return None

    companies_list: list[NSECompaniesList] = []

    paginator = soup.find("table", {"class": "pagination-container-company"})
    paginator_message = paginator.find("td").text.strip()  # type: ignore
    total_companies = re.findall(r"Showing 1 - 200 of (\d+)", paginator_message)

    if total_companies:
        total_companies = int(total_companies[0])
    else:
        print("Failed to extract total companies count")
        return None

    last_page_start = ((total_companies // 200) * 200) + 1
    all_pages_range = f"{last_page_start + 200}-{last_page_start + 399}"

    # Get All Companies
    all_coompanies_soup = _get_url_soup(
        f"{conf.NSE_COMPANIES_LIST_REDIFF_URL}{all_pages_range}"
    )

    # Get Data Table
    companies_tables = all_coompanies_soup.find_all("table", {"class": "dataTable"})  # type: ignore

    # For every table find rows
    for companies_table in companies_tables:
        rows = companies_table.find_all("tr")  # type: ignore

        for row in rows:
            cols = row.find_all("td")  # type: ignore

            # Continue if there are data columns less than 2
            if len(cols) < 2:
                continue

            symbol = cols[0].text.strip()
            company_name = cols[1].text.strip()

            companies_list.append(
                NSECompaniesList(symbol=symbol, companyName=company_name)
            )

    return companies_list


def get_nse_companies_list_from_wikipedia() -> list[NSECompaniesList] | None:
    soup = _get_url_soup(conf.NSE_COMPANIES_WIKIPEDIA_URL)
    if soup is None:
        return None

    companies_list: list[NSECompaniesList] = []

    tables = soup.find_all("table")

    for table in tables:
        head = table.find_all("th")  # type: ignore
        heads = ",".join([h.text.strip() for h in head])

        # Skip tables where sumbol and companyname is not given
        if heads != "Symbol,Company name":
            continue

        # Get all rows in table with Data
        rows = table.find_all("tr")  # type: ignore

        for row in rows:
            cols = row.find_all("td")  # type: ignore

            # Continue if there are data columns less than 2
            if len(cols) < 2:
                continue

            symbol = cols[0].text.strip().lstrip("NSE:").strip()
            company_name = cols[1].text.strip()

            companies_list.append(
                NSECompaniesList(symbol=symbol, companyName=company_name)
            )

    return companies_list
