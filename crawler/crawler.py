from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from core.logger import logger


def crawl_site(start_url, max_pages=20):
    visited = set()
    to_visit = [start_url]
    collected = []

    domain = urlparse(start_url).netloc  # Domain restriction
    logger.info(f"[STATIC CRAWLER] Starting crawl at {start_url} (max_pages={max_pages})")

    while to_visit and len(collected) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        visited.add(url)
        logger.info(f"[STATIC CRAWLER] Visiting: {url}")

        try:
            r = requests.get(url, timeout=10)
            r.encoding = "utf-8"   # 🔧 FIX HERE
            soup = BeautifulSoup(r.text, "lxml")
            r.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"[STATIC CRAWLER] Failed to fetch {url}: {e}")
            continue

        collected.append(url)

        soup = BeautifulSoup(r.text, "lxml")
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if urlparse(link).netloc == domain and link not in visited:
                to_visit.append(link)

    logger.info(f"[STATIC CRAWLER] Crawl completed. Pages collected: {len(collected)}")
    return collected
