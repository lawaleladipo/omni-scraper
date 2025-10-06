import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from omni_scraper.config.settings import config
from omni_scraper.core.tor_manager import TorManager
from omni_scraper.utils.logger import logger


class SessionManager:
    """
    Manages HTTP sessions with optional Tor proxy integration.
    Handles retries, proxy setup, and user-agent headers for resilience.
    """

    def __init__(self, use_tor=True):
        self.use_tor = use_tor
        self.tor = TorManager() if use_tor else None
        self.session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(
                ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
            ),
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        self.session.headers.update(
            {"User-Agent": config.get("crawler.user_agent") or "OmniScraper/0.3"}
        )

        if use_tor:
            socks = self.tor.get_socks_url()
            self.session.proxies.update(
                {"http": socks, "https": socks}
            )
            logger.info(f"Session initialized with Tor SOCKS proxy: {socks}")
        else:
            logger.info("Session initialized without Tor proxy.")

    def get_session(self):
        """
        Returns the current requests.Session object.
        This provides testable access to the configured session instance.
        """
        return self.session

