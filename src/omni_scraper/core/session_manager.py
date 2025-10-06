import requests
from requests.adapters import HTTPAdapter, Retry
from ..config.settings import config
from ..utils.logger import setup_logger
from .tor_manager import TorManager

logger = setup_logger(__name__)

class SessionManager:
    def __init__(self, use_tor=True):
        self.use_tor = use_tor
        self.tor = TorManager() if use_tor else None
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504], allowed_methods=frozenset(['GET','POST','PUT','DELETE','HEAD','OPTIONS']))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.headers.update({'User-Agent': config.get('crawler.user_agent') or 'OmniScraper/0.3'})
        if use_tor:
            socks = self.tor.get_socks_url()
            self.session.proxies.update({'http': socks, 'https': socks})

    def renew_tor(self):
        if not self.use_tor:
            logger.debug("Tor not enabled")
            return False
        return self.tor.renew_identity()

    def get(self, url, **kwargs):
        timeout = kwargs.pop('timeout', config.get('crawler.request_timeout', 30))
        try:
            r = self.session.get(url, timeout=timeout, **kwargs)
            r.raise_for_status()
            return r
        except Exception as e:
            logger.warning(f"GET failed for {url}: {e}")
            raise
