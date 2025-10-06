import time

import requests

from ..config.settings import config
from ..core.session_manager import SessionManager
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BreachChecker:
    def __init__(self, session: SessionManager = None):
        self.config = config.get("intelx") or {}
        self.base_url = "https://free.intelx.io"
        self.api_key = self.config.get("api_key", "")
        self.rate_limit_delay = float(self.config.get("rate_limit_delay", 1.0))
        self.session_manager = session or SessionManager(use_tor=False)

    def _headers(self):
        headers = {
            "User-Agent": self.config.get("user_agent", "OmniScraper/0.3"),
            "Accept": "application/json",
        }
        if self.api_key:
            headers["X-Key"] = self.api_key
        else:
            logger.warning("No Intelligence X key—limited to 50/day. Get at intelx.io")
        return headers

    def check_email(self, email):
        if not email:
            raise ValueError("Email required")
        url = f"{self.base_url}/search"
        params = {
            "term": email,
            "buckets": 1,
            "terminate": ["email", "domain"],
            "limit": 10,
            "timeout": 5,
        }
        try:
            resp = self.session_manager.get(url, params=params, headers=self._headers())
            data = resp.json()
            time.sleep(self.rate_limit_delay)
            leaks = data.get("records", [])
            logger.info(f"Intelligence X: {email} -> {len(leaks)} leaks")
            return [
                {
                    "email": email,
                    "source": leak.get("title"),
                    "date": leak.get("date"),
                    "snippet": leak.get("content", "")[:200],
                }
                for leak in leaks
            ]
        except requests.exceptions.HTTPError as he:
            if he.response.status_code == 404:
                logger.info(f"No leaks for {email}")
                return []
            elif he.response.status_code == 429:
                logger.warning("Rate limit; sleeping")
                time.sleep(self.rate_limit_delay * 2)
                return self.check_email(email)
            else:
                logger.exception(f"Intelligence X error for {email}: {he}")
                raise
        except Exception as e:
            logger.exception(f"Intelligence X unhandled error for {email}: {e}")
            raise
