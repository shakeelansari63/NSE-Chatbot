from pprint import pprint

from .config import BASE_URL
from .helper import _get_nse_client


def test_api_data(api_path: str) -> None:
    client = _get_nse_client()
    data = client.get_nse_data(f"{BASE_URL}{api_path}")
    pprint(data)
