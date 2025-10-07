# Omni-Scraper v0.1.0

Async OSINT toolkit for Tor .onion crawling, Intelligence X leak checks, Shodan lookups, and scraping. Ethical leak hunting (e.g., @company.com).

## Intelligence X Logo

/ )( )( / ) / ) / )(  _ (  )(  _ 
( (  ) ) / / ( (  _ \ )   / ) _)  )   /
_)() _/ _)(/(___)(_)(_)


Free leak search engine—50/day with key.

## OpSec/Legal Reminders (MANDATORY)
- **Legal:** Authorized cybersecurity/OSINT only. Comply with GDPR/CFAA. No unauthorized access/disruption. Document scans; get approval.
- **OpSec:** Run in VM (Whonix/Tails). .env secrets (git ignore). Mask PII in logs/exports. Tor-only traffic. Rotate circuits. Graceful shutdown on anomalies.
- **Disclaimer:** Not liable for misuse. Ethical = proactive defense, not offense.

## Quick Start
1. `pip install -e .`
2. `cp .env.example .env; nano .env` (keys)
3. `echo "company.com" > mydomain.txt`
4. `omni-scraper crawl https://company.com --no-tor`
5. `omni-scraper breach-check admin@company.com`  # Intelligence X leaks
6. `omni-scraper shodan-search "port:80" --limit 5`

## Features
- Async Tor crawler (aiohttp-socks, concurrency 4).
- Intelligence X leak search (free tier, 50/day).
- Shodan integration (host/search/vulns).
- YAML config, rotating logs (Loguru).
- Outputs: JSON/CSV with timestamps.
- Docker, pytest (async tests), CI badges.

[![CI](https://github.com/lawaleladipo/omni-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/lawaleladipo/omni-scraper/actions)

## Docker
`docker build -t omni-scraper docker/`
`docker run -v omnisraper.db:/app/db -e INTELX_API_KEY=key omni-scraper crawl`

## Tests
`pytest -q`

## Contributing
Use templates for Issues/PRs. Run `pytest` before push.

License: MIT
