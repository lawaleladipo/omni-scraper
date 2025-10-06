import asyncio
import subprocess
import sys
from pathlib import Path

import click

from .config.settings import config
from .modules.async_scraper import AsyncScraper
from .modules.async_web_crawler import AsyncWebCrawler
from .modules.breach_checker import BreachChecker
from .modules.shodan_lookup import ShodanLookup
from .utils.logger import setup_logger
from .utils.output_handler import OutputHandler

logger = setup_logger(__name__)
output_handler = OutputHandler()


@click.group()
def cli():
    """Omni-Scraper — async OSINT CLI (crawl, scrape, breach-check, shodan)."""
    pass


@cli.command("crawl")
@click.argument("seeds", nargs=-1)
@click.option("-d", "--max-depth", "max_depth", type=int, default=None)
@click.option("-m", "--max-pages", "max_pages", type=int, default=None)
@click.option("-c", "--concurrency", type=int, default=None)
@click.option("--no-tor", is_flag=True)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "csv"]))
def crawl_cmd(seeds, max_depth, max_pages, concurrency, no_tor, fmt):
    """Crawl seeds (accepts multiple). Example: omni-scraper crawl http://abc.onion"""
    if not seeds:
        seeds = tuple(config.get("crawler.seeds", []))
        if not seeds:
            click.echo("No seeds. Example: omni-scraper crawl http://example.onion")
            sys.exit(2)
    seeds = list(seeds)
    click.echo(f"[+] Crawling seeds: {seeds}")
    if not no_tor:
        subprocess.run(["sudo", "systemctl", "start", "tor"], check=False)
    crawler = AsyncWebCrawler(
        seeds=seeds,
        concurrency=concurrency,
        max_depth=max_depth,
        max_pages=max_pages,
        use_tor=not no_tor,
    )
    try:
        results = asyncio.run(crawler.run())
        output_handler.format = fmt
        out_path = output_handler.save("crawl_results", results)
        click.echo(f"[+] Saved to {out_path}")
    except Exception as e:
        logger.exception(f"Crawl failed: {e}")
        click.echo(f"[-] Failed: {e}")
        sys.exit(1)


@cli.command("scrape")
@click.argument("url")
@click.option("-s", "--save-html", is_flag=True)
@click.option("--no-tor", is_flag=True)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "csv"]))
def scrape_cmd(url, save_html, no_tor, fmt):
    """Scrape a single URL and extract emails, links, snippet."""
    click.echo(f"[+] Scraping {url}")
    if not no_tor:
        subprocess.run(["sudo", "systemctl", "start", "tor"], check=False)
    scraper = AsyncScraper(use_tor=not no_tor)
    html_path = None
    if save_html:
        safe_name = url.replace("://", "_").replace("/", "_")
        html_path = (
            Path(config.get("output.directory", "data/outputs")) / f"{safe_name}.html"
        )
        html_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = asyncio.run(
            scraper.scrape(
                url,
                save_html=save_html,
                html_path=str(html_path) if html_path else None,
            )
        )
        output_handler.format = fmt
        out_path = output_handler.save("scrape_result", result)
        click.echo(f"[+] Saved to {out_path}")
    except Exception as e:
        logger.exception(f"Scrape failed: {e}")
        click.echo(f"[-] Failed: {e}")
        sys.exit(1)


@cli.command("breach-check")
@click.argument("email")
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "csv"]))
def breach_cmd(email, fmt):
    """Check email against Intelligence X leaks."""
    click.echo(f"[+] Checking Intelligence X for {email}")
    try:
        bc = BreachChecker()
        data = bc.check_email(email)
        output_handler.format = fmt
        out_path = output_handler.save("intelx_results", {email: data})
        click.echo(f"[+] Saved to {out_path}")
    except Exception as e:
        logger.exception(f"Intelligence X check failed: {e}")
        click.echo(f"[-] Failed: {e}")
        sys.exit(1)


@cli.command("shodan-search")
@click.argument("query")
@click.option("-l", "--limit", type=int, default=10)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "csv"]))
def shodan_search_cmd(query, limit, fmt):
    """Search Shodan for a query (requires SHODAN_API_KEY)."""
    click.echo(f"[+] Running Shodan search: {query}")
    try:
        s = ShodanLookup()
        results = s.host_search(query, limit=limit)
        output_handler.format = fmt
        out_path = output_handler.save("shodan_search", results)
        click.echo(f"[+] Saved to {out_path}")
    except Exception as e:
        logger.exception(f"Shodan search failed: {e}")
        click.echo(f"[-] Failed: {e}")
        sys.exit(1)


@cli.command("shodan-host")
@click.argument("ip")
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "csv"]))
def shodan_host_cmd(ip, fmt):
    """Get Shodan host details for IP (requires SHODAN_API_KEY)."""
    click.echo(f"[+] Shodan host lookup: {ip}")
    try:
        s = ShodanLookup()
        info = s.host_lookup(ip)
        output_handler.format = fmt
        out_path = output_handler.save("shodan_host", info)
        click.echo(f"[+] Saved to {out_path}")
    except Exception as e:
        logger.exception(f"Shodan host failed: {e}")
        click.echo(f"[-] Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()

# Backward compatibility for tests expecting create_parser
def create_parser():
    return cli
