from enum import StrEnum, auto
from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel


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
    chartTodayPath: Any | None = None


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
    debtSeries: list[Any]
    isFNOSec: bool
    isCASec: bool
    isSLBSec: bool
    isDebtSec: bool
    isSuspended: bool
    tempSuspendedSeries: list[Any]
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


class OrderBookAskBidInfo(FlexibleBaseModel):
    price: float
    quantity: float


class OrderBookTradeInfo(FlexibleBaseModel):
    activeSeries: str = "EQ"
    cmAnnualVolatility: str | float = "0"
    cmDailyVolatility: str | float = "0"
    ffmc: float = 0
    impactCost: float = 0
    totalMarketCap: float = 0
    totalTradedValue: float = 0
    totalTradedVolume: float = 0


class MarketDepotOrderBookInfo(FlexibleBaseModel):
    bid: list[OrderBookAskBidInfo]
    ask: list[OrderBookAskBidInfo]
    open: float
    totalBuyQuantity: float
    totalSellQuantity: float
    tradeInfo: OrderBookTradeInfo


class SecurityWiseDelPosInfo(FlexibleBaseModel):
    deliveryQuantity: float
    deliveryToTradedQuantity: float
    quantityTraded: float
    secWiseDelPosDate: str
    seriesRemarks: Any


class StockTradeDetailResponse(FlexibleBaseModel):
    bulkBlockDeals: list[Any]
    marketDeptOrderBook: MarketDepotOrderBookInfo
    noBlockDeals: Any
    securityWiseDP: SecurityWiseDelPosInfo


class StockDetailResponse(FlexibleBaseModel):
    info: StockInfo
    metadata: Any
    securityInfo: Any
    sddDetails: Any
    currentMarketType: str
    priceInfo: PriceInfo
    industryInfo: IndustryInfo
    preOpenMarket: PreOpenMarket
    tradeInfo: OrderBookTradeInfo


class StockDetailMcpResponse(FlexibleBaseModel):
    info: StockInfo
    currentMarketType: str
    priceInfo: PriceInfo
    industryInfo: IndustryInfo
    preOpenMarket: PreOpenMarket


class MarketSymbolMcpResponse(FlexibleBaseModel):
    symbol: str
    identifier: str


class StockHistoryData(FlexibleBaseModel):
    chSymbol: str
    chSeries: str
    mtimestamp: str
    chTradeHighPrice: float
    chTradeLowPrice: float
    chOpeningPrice: float
    chClosingPrice: float


class StockHistoryDataResponse(RootModel[list[StockHistoryData]]):
    pass


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


class CorporateBoardMeetingData(FlexibleBaseModel):
    meetingdate: str
    purpose: str
    symbol: str


class CorporateBoardMeetingInfo(FlexibleBaseModel):
    data: list[CorporateBoardMeetingData]


class CorporateActionsData(FlexibleBaseModel):
    exdate: str
    purpose: str
    symbol: str


class CorporateActionsInfo(FlexibleBaseModel):
    data: list[CorporateActionsData]


class CorporateFinancialResultsData(FlexibleBaseModel):
    from_date: str | None
    to_date: str | None
    income: str | float | None
    expenditure: str | float | None
    reProLossBefTax: str | float | None
    proLossAftTax: str | float | None
    reDilEPS: str | float | None


class CorporateFinancialResultsInfo(FlexibleBaseModel):
    data: list[CorporateFinancialResultsData]


class CorporateLatestAnnouncementsData(FlexibleBaseModel):
    broadcastdate: str
    subject: str
    symbol: str


class CorporateLatestAnnouncementsInfo(FlexibleBaseModel):
    data: list[CorporateLatestAnnouncementsData]


class CorporateShareHoldingPatternInfo(FlexibleBaseModel):
    data: dict[str, list[dict[str, str]]]


class CorporateFilingInfoResponse(FlexibleBaseModel):
    borad_meeting: CorporateBoardMeetingInfo
    corporate_actions: CorporateActionsInfo
    financial_results: CorporateFinancialResultsInfo
    latest_announcements: CorporateLatestAnnouncementsInfo
    shareholdings_patterns: CorporateShareHoldingPatternInfo
