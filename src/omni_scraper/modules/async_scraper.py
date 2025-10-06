from aiohttp_socks import ProxyConnector
import aiohttp
from bs4 import BeautifulSoup
from ..utils.logger import setup_logger
from ..config.settings import config
from ..utils.helpers import extract_emails, normalize_url, is_onion

logger = setup_logger(__name__)

class AsyncScraper:
    def __init__(self, use_tor=True):
        self.cfg = config.get('crawler') or {}
        self.timeout = int(self.cfg.get('request_timeout', 30))
        self.delay = float(self.cfg.get('request_delay', 1))
        self.user_agent = self.cfg.get('user_agent', 'OmniScraper-Scraper/async')
        self.use_tor = use_tor
        self.proxy_url = f"socks5h://127.0.0.1:{config.get('tor.socks_port', 9050)}"

    async def scrape(self, url, save_html=False, html_path=None):
        connector = ProxyConnector.from_url(self.proxy_url) if self.use_tor else None
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        headers = {'User-Agent': self.user_agent}
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        logger.warning(f"Scrape non-200 {url}: {resp.status}")
                        return {'url': url, 'status': resp.status, 'error': f"Status {resp.status}"}
                    html = await resp.text(errors='ignore')
                    if save_html and html_path:
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(html)
                    text = BeautifulSoup(html, 'html.parser').get_text(separator=' ')
                    emails = extract_emails(text)
                    links = [normalize_url(url, a['href']) for a in BeautifulSoup(html, 'html.parser').find_all('a', href=True) if is_onion(normalize_url(url, a['href']))]
                    snippet = text.strip()[:5000]
                    return {'url': url, 'status': resp.status, 'emails': emails, 'links': links, 'snippet': snippet}
            except Exception as e:
                logger.exception(f"Scrape failed for {url}: {e}")
                return {'url': url, 'status': None, 'error': str(e)}
