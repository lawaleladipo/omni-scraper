from omni_scraper.modules.shodan_lookup import ShodanLookup

def test_shodan_lookup_creation():
    lookup = ShodanLookup()
    assert lookup is not None
