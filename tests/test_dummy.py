import pytest
from omni_scraper.modules.async_web_crawler import AsyncWebCrawler
from omni_scraper.utils.helpers import extract_emails, is_onion

def test_extract_emails():
    text = "Contact us at test@example.com or admin@lbs.edu.ng"
    emails = extract_emails(text)
    assert "admin@lbs.edu.ng" in emails

def test_is_onion():
    assert is_onion("http://test.onion/") == True
    assert is_onion("http://test.com/") == False

@pytest.mark.asyncio
async def test_crawler_run():
    crawler = AsyncWebCrawler(seeds=["http://example.com"], use_tor=False, max_pages=1)
    results = await crawler.run()
    assert len(results) > 0
