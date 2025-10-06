import time
from stem import Signal
from stem.control import Controller
from omni_scraper.config.settings import config
from omni_scraper.utils.logger import logger


class TorManager:
    """
    Manages Tor identity renewal and proxy configuration for the OmniScraper project.
    Handles circuit renewal, proxy settings, and retry logic with configurable parameters.
    """

    def __init__(self):
        tor_cfg = config.get("tor")
        self.control_port = tor_cfg.get("control_port", 9051)
        self.socks_port = tor_cfg.get("socks_port", 9050)
        self.tor_port = self.socks_port  # Alias for backward compatibility with tests
        self.password = tor_cfg.get("password")
        self.retry_count = 0
        self.max_retries = tor_cfg.get("max_retries", 3)

    def renew_identity(self):
        """
        Sends a NEWNYM signal to the Tor controller to request a new circuit.
        Returns True if successful, otherwise False.
        """
        try:
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate(password=self.password)
                controller.signal(Signal.NEWNYM)
                logger.info("Tor circuit renewed successfully.")
                self.retry_count = 0
                return True
        except Exception as e:
            self.retry_count += 1
            logger.error(
                f"Failed to renew Tor identity (attempt {self.retry_count}/{self.max_retries}): {e}"
            )
            if self.retry_count >= self.max_retries:
                logger.critical("Max retries exceeded for Tor renewal.")
                raise
            return False

    def get_proxies(self):
        """
        Returns a dictionary of HTTP and HTTPS proxy configurations for use with requests or aiohttp.
        """
        return {
            "http": f"socks5h://127.0.0.1:{self.socks_port}",
            "https": f"socks5h://127.0.0.1:{self.socks_port}",
        }

    def get_socks_url(self):
        """
        Returns a single SOCKS5 proxy URL for use in session configuration.
        """
        return f"socks5h://127.0.0.1:{self.socks_port}"
