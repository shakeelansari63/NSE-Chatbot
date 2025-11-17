from sqlmodel import SQLModel

DbMetadata = SQLModel.metadata

# Import models here to make them available in metadata
from .nse_metadata import NSEMetadata  # noqa
