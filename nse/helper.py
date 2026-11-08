import logging
from functools import cache

from pydantic import ValidationError

from . import config as conf
from .models import (
    CorporateFilingInfoResponse,
    EquityResponseItem,
    MarketPreOpenApiResponse,
    MarketPreOpenMcp,
    MarketStatus,
    MarketStatusApiResp,
    MarketStatusMcp,
    Stock52weekAnalysis,
    Stock52WeekHighResponse,
    Stock52WeekLowResponse,
    StockHistoryData,
    StockHistoryDataResponse,
    StockWeeklyVolumeGainerResponse,
    StockWeeklyVolumeGainers,
)
from .nse_http import NSEHttpClient

logger = logging.getLogger(__name__)


@cache
def _get_nse_client() -> NSEHttpClient:
    nse_client = NSEHttpClient()
    return nse_client


def get_all_markets_state() -> list[MarketStatusMcp] | None:
    data = _get_nse_client().get_nse_data(conf.MARKET_STATUS_URL)
    if data is None or not isinstance(data, dict):
        return None

    # NSE mixes index snapshots (e.g. "NIFTY50 USD") into `marketState` that carry
    # index/last/percentChange instead of market fields, so only validate entries
    # that actually describe a market.
    market_entries = [
        entry
        for entry in data.get("marketState", [])
        if isinstance(entry, dict) and entry.get("market") and entry.get("marketStatus")
    ]

    market_state = MarketStatusApiResp.model_validate({"marketState": market_entries})

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


def get_stock_details(
    symbol: str,
    with_trade: bool = False,
) -> EquityResponseItem | None:
    data = _get_nse_client().get_nse_data(
        conf.STOCK_QUOTE_URL,
        {"functionName": "getSymbolData", "marketType": "N", "series": "EQ", "symbol": symbol},
    )

    if not isinstance(data, dict):
        return None

    entries = data.get("equityResponse")
    if not isinstance(entries, list):
        return None

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        # NSE returns a placeholder entry with all-null fields for symbols it has
        # no quote for (e.g. not yet traded today), so skip those instead of
        # failing validation for the whole response.
        if not entry.get("metaData") or not entry.get("orderBook"):
            continue

        try:
            return EquityResponseItem.model_validate(entry)
        except ValidationError:
            logger.warning(
                "Skipping invalid quote payload for symbol %s", symbol, exc_info=True
            )

    return None


def get_stock_history_for_specific_range(
    symbol: str,
    from_date: str,
    to_date: str,
) -> list[StockHistoryData] | None:
    # Get Stock Detail
    detail = get_stock_details(symbol)

    # The quote can be unavailable (e.g. symbol not traded today) even though
    # history exists, so fall back to the default equity series in that case.
    stock_series = detail.metaData.series if detail is not None else "EQ"

    # Get Stock History Data
    data = _get_nse_client().get_nse_data(
        conf.NSE_STOCK_HISTORY,
        {
            "functionName": "getHistoricalTradeData",
            "symbol": symbol,
            "series": stock_series,
            "fromDate": from_date,
            "toDate": to_date,
        },
    )

    if data is None:
        return None

    try:
        stock_history_data = StockHistoryDataResponse.model_validate(data)
    except ValidationError:
        logger.warning(
            "Unexpected historical data payload for symbol %s", symbol, exc_info=True
        )
        return None

    return stock_history_data.root


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


def get_stock_corporate_filing_info(
    symbol: str,
) -> CorporateFilingInfoResponse | None:
    data = _get_nse_client().get_nse_data(
        conf.CORPORATE_FILING_INFORMATION, {"symbol": symbol, "market": "equities"}
    )
    if data is None:
        return None

    data = CorporateFilingInfoResponse.model_validate(data)
    return data
