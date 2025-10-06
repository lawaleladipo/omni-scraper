import asyncio

import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup

from ..config.settings import config
from ..utils.helpers import extract_emails, is_onion, normalize_url
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class AsyncWebCrawler:
    def __init__(
        self, seeds=None, concurrency=None, max_depth=None, max_pages=None, use_tor=True
    ):
        self.cfg = config.get("crawler") or {}
        self.max_depth = int(max_depth or self.cfg.get("max_depth", 3))
        self.max_pages = int(max_pages or self.cfg.get("max_pages", 100))
        self.timeout = int(self.cfg.get("request_timeout", 30))
        self.delay = float(self.cfg.get("request_delay", 2))
        self.user_agent = self.cfg.get("user_agent", "OmniScraper-WebCrawler/async")
        self.seeds = seeds or self.cfg.get("seeds", [])
        self.visited = set()
        self.results = []
        self.concurrency = int(concurrency or self.cfg.get("concurrency", 4))
        self._stop_flag = asyncio.Event()
        self.use_tor = use_tor
        self.proxy_url = f"socks5h://127.0.0.1:{config.get('tor.socks_port', 9050)}"

    async def _fetch(self, session, url):
        headers = {"User-Agent": self.user_agent}
        try:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status != 200:
                    logger.warning(f"{url} -> {resp.status}")
                    return None
                text = await resp.text(errors="ignore")
                logger.info(f"Fetched {url} (len={len(text)})")
                return text
        except Exception as e:
            logger.warning(f"Fetch failed {url}: {e}")
            return None
        finally:
            await asyncio.sleep(self.delay)

    async def _worker(self, session, queue):
        while (
            not queue.empty()
            and len(self.visited) < self.max_pages
            and not self._stop_flag.is_set()
        ):
            try:
                url, depth = await queue.get()
            except asyncio.CancelledError:
                break
            if url in self.visited:
                queue.task_done()
                continue
            if depth > self.max_depth:
                queue.task_done()
                continue
            self.visited.add(url)
            html = await self._fetch(session, url)
            if html:
                snippet = html.strip()[:2000]
                emails = extract_emails(html)
                self.results.append(
                    {"url": url, "depth": depth, "emails": emails, "snippet": snippet}
                )
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    new = normalize_url(url, a["href"])
                    if new and is_onion(new) and new not in self.visited:
                        queue.put_nowait((new, depth + 1))
            queue.task_done()

    async def run(self, seeds=None):
        seeds = seeds or self.seeds or []
        if not seeds:
            logger.error("No seeds")
            return []
        connector = ProxyConnector.from_url(self.proxy_url) if self.use_tor else None
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            queue = asyncio.Queue()
            for s in seeds:
                queue.put_nowait((s, 0))
            workers = [
                asyncio.create_task(self._worker(session, queue))
                for _ in range(self.concurrency)
            ]
            await queue.join()
            self._stop_flag.set()
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
        logger.info(
            f"Crawl complete: pages={len(self.results)} visited={len(self.visited)}"
        )
        return self.results
