from typing import Any

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


def search_nse_data_in_db(
    search_key: str,
    search_fields: list[Any],
) -> list[NSEMetadata]:
    with Session(engine) as session:
        # Output
        output: list[NSEMetadata] = []

        # Search with Likes
        for field in search_fields:
            # Search where field value starts with search key
            q_search_by_field_start = (
                select(NSEMetadata)
                .where(
                    NSEMetadata.symbol.not_in([op.symbol for op in output]),
                    func.lower(field).like(f"{search_key.lower()}%"),
                )
                .limit(3)
            )
            search_by_field_start = session.exec(q_search_by_field_start).all()
            output.extend(search_by_field_start)

            # Search where field value contains search key
            q_search_by_field_contains = (
                select(NSEMetadata)
                .where(
                    NSEMetadata.symbol.not_in([op.symbol for op in output]),
                    func.lower(field).like(f"%{search_key.lower()}%"),
                )
                .limit(3)
            )
            search_by_field_contains = session.exec(q_search_by_field_contains).all()
            output.extend(search_by_field_contains)

        # Search More with Trigram and Levenshtein similarity
        for field in search_fields:
            # Trigram Similarity
            q_search_by_trgm = (
                select(NSEMetadata)
                .where(NSEMetadata.symbol.not_in([op.symbol for op in output]))
                .order_by(func.similarity(func.lower(field), search_key.lower()).desc())
                .limit(3)
            )

            # Get 3 rows
            search_by_trgm = session.exec(q_search_by_trgm).all()
            output.extend(search_by_trgm)

            # Levenshtein Similarity
            q_search_by_lvsn_symbol = (
                select(NSEMetadata)
                .where(NSEMetadata.symbol.not_in([op.symbol for op in output]))
                .order_by(func.levenshtein(func.lower(field), search_key.lower()))
                .limit(3)
            )

            # Get 3 rows
            search_by_lvsn_symbol = session.exec(q_search_by_lvsn_symbol).all()

            # Add to output
            output.extend(search_by_lvsn_symbol)

        # Return Output
        return output


# Search NSE Company
def search_nse_company_by_name_or_symbol_indb(search_key: str) -> list[NSEMetadata]:
    return search_nse_data_in_db(
        search_key=search_key, search_fields=[NSEMetadata.name, NSEMetadata.symbol]
    )


def search_sector_or_industry_indb(search_key: str) -> list[str]:
    sector_or_industries = search_nse_data_in_db(
        search_key=search_key,
        search_fields=[
            NSEMetadata.sector,
            NSEMetadata.industry,
            NSEMetadata.industry_info,
        ],
    )
    return list(
        set(
            [sector_or_industry.industry for sector_or_industry in sector_or_industries]
        )
    )


def get_companies_in_specified_industry(
    industry_keys: list[str],
    top_n: int = 10,
) -> list[dict[str, str]]:
    with Session(engine) as session:
        q_company_in_sector_industry = (
            select(NSEMetadata)
            .where(NSEMetadata.industry.in_(industry_keys))
            .order_by(NSEMetadata.total_market_cap_in_crore.desc())
            .limit(top_n)
        )

        # Get data
        company_in_industry = [
            {row.symbol: row.name}
            for row in session.exec(q_company_in_sector_industry).all()
        ]

        return company_in_industry
