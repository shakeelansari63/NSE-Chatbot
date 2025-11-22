from enum import StrEnum, auto
from typing import Any

from pydantic import BaseModel, ConfigDict


class MarketStatus(StrEnum):
    OPEN = "Open"
    CLOSED = "Closed"
    CLOSE = "Close"


class FlexibleBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class MarketState(FlexibleBaseModel):
    market: str
    marketStatus: MarketStatus
    tradeDate: str
    index: str
    last: float | str
    variation: float | str
    percentChange: float | str
    marketStatusMessage: str


class MarketStatusApiResp(FlexibleBaseModel):
    marketState: list[MarketState]


class MarketStatusMcp(FlexibleBaseModel):
    market: str
    marketStatus: MarketStatus
    tradeDate: str
    marketStatusMessage: str


class MarketPreOpenApiResponseMetadata(FlexibleBaseModel):
    symbol: str | None
    identifier: str | None
    purpose: Any
    lastPrice: float | None
    change: float | None
    pChange: float | None
    previousClose: float | None
    finalQuantity: float | None
    totalTurnover: float | None
    marketCap: Any
    yearHigh: float | None
    yearLow: float | None
    iep: float | None
    chartTodayPath: Any


class MarketPreOpenApiResponseData(FlexibleBaseModel):
    metadata: MarketPreOpenApiResponseMetadata
    detail: Any


class MarketPreOpenApiResponse(FlexibleBaseModel):
    declines: int | None
    unchanged: float | None
    data: list[MarketPreOpenApiResponseData]
    advances: float | None
    timestamp: str | None
    totalTradedValue: float | None
    totalmarketcap: float | None
    totalTradedVolume: float | None


class MarketPreOpenMcp(FlexibleBaseModel):
    symbol: str | None
    identifier: str | None
    lastPrice: float | None
    change: float | None
    pChange: float | None
    previousClose: float | None
    finalQuantity: float | None
    totalTurnover: float | None
    yearHigh: float | None
    yearLow: float | None


class StockInfo(FlexibleBaseModel):
    symbol: str
    companyName: str
    industry: str
    activeSeries: list[str]
    debtSeries: list
    isFNOSec: bool
    isCASec: bool
    isSLBSec: bool
    isDebtSec: bool
    isSuspended: bool
    tempSuspendedSeries: list
    isETFSec: bool
    isDelisted: bool
    listingDate: str
    isMunicipalBond: bool
    isHybridSymbol: bool
    identifier: str


class Surveillance(FlexibleBaseModel):
    surv: Any
    desc: Any


class IntraDayHighLow(FlexibleBaseModel):
    min: float
    max: float
    value: float


class WeekHighLow(FlexibleBaseModel):
    min: float
    minDate: str
    max: float
    maxDate: str
    value: float


class PriceInfo(FlexibleBaseModel):
    lastPrice: float
    change: float
    pChange: float
    previousClose: float
    open: float
    close: float
    vwap: float
    stockIndClosePrice: float
    lowerCP: str
    upperCP: str
    pPriceBand: str
    basePrice: float
    intraDayHighLow: IntraDayHighLow
    weekHighLow: WeekHighLow
    iNavValue: Any
    checkINAV: bool
    tickSize: float
    ieq: str


class IndustryInfo(FlexibleBaseModel):
    macro: str
    sector: str
    industry: str
    basicIndustry: str


class PreopenItem(FlexibleBaseModel):
    price: float
    buyQty: int
    sellQty: int
    iep: bool | None = None


class Ato(FlexibleBaseModel):
    buy: int
    sell: int


class PreOpenMarket(FlexibleBaseModel):
    preopen: list[PreopenItem]
    ato: Ato
    IEP: float
    totalTradedVolume: int
    finalPrice: float
    finalQuantity: int
    lastUpdateTime: str
    totalBuyQuantity: int
    totalSellQuantity: int
    atoBuyQty: int
    atoSellQty: int
    Change: float
    perChange: float
    prevClose: float


class StockDetailResponse(FlexibleBaseModel):
    info: StockInfo
    metadata: Any
    securityInfo: Any
    sddDetails: Any
    currentMarketType: str
    priceInfo: PriceInfo
    industryInfo: IndustryInfo
    preOpenMarket: PreOpenMarket


class StockDetailMcpResponse(FlexibleBaseModel):
    info: StockInfo
    currentMarketType: str
    priceInfo: PriceInfo
    industryInfo: IndustryInfo
    preOpenMarket: PreOpenMarket


class MarketSymbolMcpResponse(FlexibleBaseModel):
    symbol: str
    identifier: str


class Stock52weekAnalysis(FlexibleBaseModel):
    symbol: str
    series: str
    comapnyName: str
    new52WHL: float
    prev52WHL: float
    prevHLDate: str
    ltp: float
    prevClose: float
    change: float
    pChange: float


class Stock52WeekHighResponse(FlexibleBaseModel):
    high: float
    data: list[Stock52weekAnalysis]
    timestamp: str | None = None


class Stock52WeekLowResponse(FlexibleBaseModel):
    low: float
    data: list[Stock52weekAnalysis]
    timestamp: str | None = None


class StockWeeklyVolumeGainers(FlexibleBaseModel):
    symbol: str
    companyName: str
    volume: float
    week1AvgVolume: float
    week1volChange: float
    week2AvgVolume: float
    week2volChange: float
    ltp: float
    pChange: float
    turnover: float


class StockWeeklyVolumeGainerResponse(FlexibleBaseModel):
    data: list[StockWeeklyVolumeGainers]
    timestamp: str | None = None


class NSECompaniesList(FlexibleBaseModel):
    symbol: str
    companyName: str


class NSECompanyListWithMatchScore(FlexibleBaseModel):
    symbol: str
    companyName: str
    nameScore: int
    symbolScore: int
