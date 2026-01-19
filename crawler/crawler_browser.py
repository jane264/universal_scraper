from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from core.logger import logger


def crawl_site_browser(start_url, max_pages=20):
    visited = set()
    collected = []
    to_visit = [start_url]

    domain = urlparse(start_url).netloc
    logger.info(f"[DYNAMIC CRAWLER] Starting browser crawl at {start_url} (max_pages={max_pages})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        while to_visit and len(collected) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue

            visited.add(url)
            logger.info(f"[DYNAMIC CRAWLER] Visiting: {url}")

            try:
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle")
            except Exception as e:
                logger.warning(f"[DYNAMIC CRAWLER] Failed to load {url}: {e}")
                continue

            collected.append(url)

            for a in page.query_selector_all("a[href]"):
                href = a.get_attribute("href")
                if not href:
                    continue
                full = urljoin(url, href)
                if urlparse(full).netloc == domain and full not in visited:
                    to_visit.append(full)

        browser.close()

    logger.info(f"[DYNAMIC CRAWLER] Crawl completed. Pages collected: {len(collected)}")
    return collected
