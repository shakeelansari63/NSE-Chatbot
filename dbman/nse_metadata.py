from sqlmodel import Field, SQLModel


class NSEMetadata(SQLModel, table=True):
    __tablename__ = "nse_metadata"
    symbol: str = Field(index=True, primary_key=True)
    name: str
    sector: str
    industry: str
