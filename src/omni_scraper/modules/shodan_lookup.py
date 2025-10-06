import shodan

from ..config.settings import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ShodanLookup:
    def __init__(self):
        api_key = config.get("shodan.api_key")
        if not api_key:
            raise ValueError(
                "SHODAN_API_KEY not configured. Set in .env or config/default.yaml"
            )
        self.client = shodan.Shodan(api_key)

    def host_search(self, query, limit=10):
        """Run a basic Shodan search query (returns a list of matches)."""
        results = []
        try:
            res = self.client.search(query, limit=limit)
            for match in res.get("matches", []):
                results.append(
                    {
                        "ip_str": match.get("ip_str"),
                        "port": match.get("port"),
                        "org": match.get("org"),
                        "data": match.get("data")[:500],  # trim
                    }
                )
            logger.info(f"Shodan: query={query} results={len(results)}")
            return results
        except Exception as e:
            logger.exception(f"Shodan search failed: {e}")
            raise

    def host_lookup(self, ip):
        """Get detailed host info."""
        try:
            info = self.client.host(ip)
            logger.info(f"Shodan host lookup: {ip}")
            return info
        except Exception as e:
            logger.exception(f"Shodan lookup failed for {ip}: {e}")
            raise
