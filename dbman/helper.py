from sqlmodel import Session, create_engine, func, select

from server_config import get_server_config as sc

from .nse_metadata import NSEMetadata

engine = create_engine(sc().pg_url, connect_args={"connect_timeout": 30})


# Add or update NSE Metadata
def save_nse_metadata(metadata: NSEMetadata):
    with Session(engine) as session:
        # Check if metadata already exist
        q_existing_metadata = select(NSEMetadata).where(
            NSEMetadata.symbol == metadata.symbol
        )
        existing_metadata = session.exec(q_existing_metadata).first()

        # Check if metadata already exist
        if existing_metadata:
            existing_metadata.sqlmodel_update(metadata)
        else:
            session.add(metadata)

        # Save Changes
        session.commit()


# Delete Outdated Symbols
def delete_outdated_symbols(symbols: list[str]):
    with Session(engine) as session:
        q_outdated_symbols = select(NSEMetadata).where(
            NSEMetadata.symbol.not_in(symbols)
        )
        outdated_symbols = session.exec(q_outdated_symbols).all()

        # Delete outdated symbols
        for outdated_symbol in outdated_symbols:
            session.delete(outdated_symbol)

        # Save Changes
        session.commit()


# Search NSE Company
def search_nse_company_indb(search_key: str) -> list[NSEMetadata]:
    with Session(engine) as session:
        # Output
        output: list[NSEMetadata] = []

        # Find Top 2 Companies where name starts with search key
        q_search_by_name_starts_with = (
            select(NSEMetadata)
            .where(func.lower(NSEMetadata.name).like(f"{search_key.lower()}%"))
            .limit(2)
        )

        search_by_name_starts_with = session.exec(q_search_by_name_starts_with).all()

        # Add to output
        output.extend(search_by_name_starts_with)

        # Find Top 2 Companies where name contains search key
        q_search_by_name_contains = (
            select(NSEMetadata)
            .where(
                NSEMetadata.symbol.not_in([op.symbol for op in output]),
                func.lower(NSEMetadata.name).like(f"%{search_key.lower()}%"),
            )
            .limit(2)
        )

        search_by_name_contains = session.exec(q_search_by_name_contains).all()

        # Add to output
        output.extend(search_by_name_contains)

        # Find top 2 with trigram similarity in Name
        q_search_by_trgm_name = (
            select(NSEMetadata)
            .where(NSEMetadata.symbol.not_in([op.symbol for op in output]))
            .order_by(
                func.similarity(func.lower(NSEMetadata.name), search_key.lower()).desc()
            )
            .limit(2 if len(output) >= 4 else 3)
        )

        # Get 2 rows
        search_by_trgm_name = session.exec(q_search_by_trgm_name).all()

        # Add to output
        output.extend(search_by_trgm_name)

        # Find top 2 with trigram similarity in Symbol
        q_search_by_trgm_symbol = (
            select(NSEMetadata)
            .where(NSEMetadata.symbol.not_in([op.symbol for op in output]))
            .order_by(
                func.similarity(
                    func.lower(NSEMetadata.symbol), search_key.lower()
                ).desc()
            )
            .limit(2 if len(output) >= 6 else 3)
        )

        search_by_trgm_symbol = session.exec(q_search_by_trgm_symbol).all()

        # Add to output
        output.extend(search_by_trgm_symbol)

        # Find top 2 with levenshtein distance in Name
        q_search_by_lvsn_name = (
            select(NSEMetadata)
            .where(NSEMetadata.symbol.not_in([op.symbol for op in output]))
            .order_by(
                func.levenshtein(func.lower(NSEMetadata.name), search_key.lower())
            )
            .limit(2 if len(output) >= 8 else 3)
        )

        search_by_lvsn_name = session.exec(q_search_by_lvsn_name).all()

        # Add to output
        output.extend(search_by_lvsn_name)

        # Find top 2 with levenshtein distance in Symbol
        q_search_by_lvsn_symbol = (
            select(NSEMetadata)
            .where(NSEMetadata.symbol.not_in([op.symbol for op in output]))
            .order_by(
                func.levenshtein(func.lower(NSEMetadata.symbol), search_key.lower())
            )
            .limit(2 if len(output) >= 10 else 3)
        )

        search_by_lvsn_symbol = session.exec(q_search_by_lvsn_symbol).all()

        # Add to output
        output.extend(search_by_lvsn_symbol)

        # Give final output
        return output


def get_unique_sectors_and_industries() -> list[str]:
    with Session(engine) as session:
        q_sector = select(NSEMetadata.sector).group_by(NSEMetadata.sector)
        q_industries = select(NSEMetadata.industry).group_by(NSEMetadata.industry)
        q_industry_info = select(NSEMetadata.industry_info).group_by(
            NSEMetadata.industry_info
        )
        q_sector_industries = q_sector.union(q_industries, q_industry_info)

        sector_industries: list[str] = [
            row[0] for row in session.exec(q_sector_industries).all()
        ]

        return sector_industries


def get_companies_in_sectors_or_industries(
    sectors_or_industries: list[str],
    top_n: int = 10,
) -> list[dict[str, str]]:
    with Session(engine) as session:
        q_company_in_sector_industry = (
            select(NSEMetadata)
            .where(
                (NSEMetadata.sector.in_(sectors_or_industries))
                | (NSEMetadata.industry.in_(sectors_or_industries))
                | (NSEMetadata.industry_info.in_(sectors_or_industries))
            )
            .order_by(NSEMetadata.total_market_cap_in_crore.desc())
            .limit(top_n)
        )

        # Get data
        company_in_sector_industry = [
            {row.symbol: row.name}
            for row in session.exec(q_company_in_sector_industry).all()
        ]

        return company_in_sector_industry
