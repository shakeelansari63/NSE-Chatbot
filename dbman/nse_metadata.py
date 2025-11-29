from sqlmodel import Field, SQLModel


class NSEMetadata(SQLModel, table=True):
    __tablename__ = "nse_metadata"
    symbol: str = Field(index=True, primary_key=True)
    name: str
    sector: str
    industry: str
    industry_info: str
    total_traded_volume_in_lakhs: float = Field(default=0)
    total_traded_value_in_crore: float = Field(default=0)
    total_market_cap_in_crore: float = Field(default=0)
