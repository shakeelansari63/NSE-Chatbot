import logging
import threading
import time
import urllib.parse
from typing import Any

import httpx
from httpx_retries import Retry, RetryTransport

from server_config import get_server_config as sc

from . import config as conf

logger = logging.getLogger(__name__)

_MIN_REQUEST_INTERVAL = 0.3  # seconds between NSE API requests


class NSEHttpClient:
    def __init__(self):
        # Set Retry transport for Httpx
        retry: Retry = Retry(total=3, backoff_factor=0.5)
        self.retry_transport: RetryTransport = RetryTransport(retry=retry)
        self._cookie_lock = threading.Lock()
        self._rate_lock = threading.Lock()
        self._last_request_time = 0.0

        # Set Initial Cookie
        self._set_nse_cookies()

    def _throttle(self):
        """Ensure minimum interval between successive requests."""
        with self._rate_lock:
            elapsed = time.time() - self._last_request_time
            if elapsed < _MIN_REQUEST_INTERVAL:
                time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
            self._last_request_time = time.time()

    def _set_nse_cookies(self):
        """
        This method is used to set the cookies required for NSE API requests.
        It initializes a session and fetches the cookies from the base URL.
        """
        client = httpx.Client(transport=self.retry_transport)
        client.headers.update(conf.NSE_HEADER)
        client.get(f"{conf.EQUITY_URL}{sc().test_symbol}")
        with self._cookie_lock:
            self.cookies = client.cookies

    def _check_cookie_expired(self):
        """
        This method checks if the cookies have expired.
        If they have, it reinitializes the session and fetches new cookies.
        """
        with self._cookie_lock:
            if not self.cookies or not self.cookies.jar:
                self._set_nse_cookies()
                return

            for cookie in self.cookies.jar:
                if cookie.is_expired():
                    self._set_nse_cookies()
                    break

    def _get_http_client(self):
        """
        This method returns the HTTP/2 client with the current cookies.
        It checks if the cookies are expired before returning the client.
        """
        self._check_cookie_expired()
        with self._cookie_lock:
            cookies = self.cookies
        return httpx.Client(
            cookies=cookies,
            headers=conf.NSE_HEADER,
            transport=self.retry_transport,
        )

    def get_nse_data(
        self,
        url: str,
        params: dict[str, str] | None = None,
    ) -> Any | None:
        """
        This method fetches data from the given NSE URL.
        It returns the JSON response if successful, or None if there is an error.
        """
        if params is not None and len(params) > 0:
            url_params = urllib.parse.urlencode(params)
            url = f"{url}?{url_params}"

        try:
            self._throttle()
            client = self._get_http_client()
            response = client.get(url)

            # Implement retry with cookie refresh if 403 error - Attempt 1
            if response.status_code == 403:
                time.sleep(1)
                self._set_nse_cookies()
                client = self._get_http_client()
                response = client.get(url)

            # Implement retry with cookie refresh if 403 error - Attempt 2
            if response.status_code == 403:
                time.sleep(2)
                self._set_nse_cookies()
                client = self._get_http_client()
                response = client.get(url)

            response.raise_for_status()
            return response.json()
        except httpx.ReadTimeout:
            logger.warning("Failed to read NSE data after multiple retries: %s", url)
            return None
        except httpx.HTTPStatusError as e:
            logger.warning("HTTP error fetching NSE data: %s - %s", url, e.response.status_code)
            return None
        except Exception as e:
            logger.exception("Unexpected error fetching NSE data: %s", url)
            return None
