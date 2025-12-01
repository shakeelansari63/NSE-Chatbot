from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from dbman.nse_metadata import NSEMetadata
from nse.helper import get_all_market_pre_open, get_stock_details

from .helper import delete_outdated_symbols, save_nse_metadata


def task_executor(symbol: str):
    stock_detail = get_stock_details(symbol, with_trade=True)
    if stock_detail is None:
        return

    # Save the metadat to Database
    save_nse_metadata(
        NSEMetadata(
            symbol=symbol,
            name=stock_detail.info.companyName,
            sector=stock_detail.industryInfo.sector,
            industry=stock_detail.industryInfo.industry,
            industry_info=stock_detail.industryInfo.basicIndustry,
            total_traded_volume_in_lakhs=stock_detail.tradeInfo.totalTradedVolume,
            total_traded_value_in_crore=stock_detail.tradeInfo.totalTradedValue,
            total_market_cap_in_crore=stock_detail.tradeInfo.totalMarketCap,
            refresh_dtm=datetime.now(),
        )
    )


def refresh_market_metadata():
    market_data = get_all_market_pre_open()

    # Skip if no market data found
    if market_data is None:
        return

    # Get list of market symbols
    market_symbols = [
        market.symbol for market in market_data if market.symbol is not None
    ]

    # Run in multi thread to get and save metadata
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(task_executor, market_symbols)

    # Delete Outdated Symbols
    delete_outdated_symbols(market_symbols)
