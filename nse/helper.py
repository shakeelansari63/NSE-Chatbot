from functools import cache

from . import config as conf
from .models import (
    MarketPreOpenApiResponse,
    MarketPreOpenMcp,
    MarketStatus,
    MarketStatusApiResp,
    MarketStatusMcp,
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


def get_all_markets_state() -> list[MarketStatusMcp] | None:
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


def get_capital_market_state() -> MarketStatus | None:
    all_market_state = get_all_markets_state()
    if all_market_state is None:
        return None

    equity_market_state = list(
        filter(lambda x: x.market == "Capital Market", all_market_state)
    )
    if not equity_market_state:
        return None

    return equity_market_state[0].marketStatus


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
    data = _get_nse_client().get_nse_data(conf.STOCKS_52_HIGH)
    if data is None:
        return None
    data = Stock52WeekHighResponse.model_validate(data)
    return data.data


def get_stock_running_52week_low() -> list[Stock52weekAnalysis] | None:
    data = _get_nse_client().get_nse_data(conf.STOCKS_52_LOW)
    if data is None:
        return None
    data = Stock52WeekLowResponse.model_validate(data)
    return data.data


def get_weekly_volume_gainers() -> list[StockWeeklyVolumeGainers] | None:
    data = _get_nse_client().get_nse_data(conf.WEEKLY_VOLUME_GAINERS)
    if data is None:
        return None
    data = StockWeeklyVolumeGainerResponse.model_validate(data)
    return data.data
