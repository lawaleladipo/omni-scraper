import re
from urllib.parse import urljoin, urlparse

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def extract_emails(text):
    if not text:
        return []
    return list(set(EMAIL_RE.findall(text)))


def normalize_url(base, link):
    try:
        return urljoin(base, link)
    except Exception:
        return None


def is_onion(url):
    try:
        parsed = urlparse(url)
        return parsed.hostname and parsed.hostname.endswith(".onion")
    except Exception:
        return False
