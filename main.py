import time
from core.logger import logger

from core.utils import (
    analyze_page_structure,
    ask_user_choice,
    content_score
)

from scrapers.api_scraper import scrape_via_api
from scrapers.static_scraper import scrape_static
from scrapers.dynamic_scraper import scrape_dynamic

from processing.content_extractor import extract_meaningful_content
from exporters.txt_exporter import export_txt

from crawler.crawler import crawl_site
from crawler.crawler_browser import crawl_site_browser

# ✅ IMPORT ALL CONFIG VARIABLES
from config import (
    MAX_PAGES,
    STATIC_SCORE_THRESHOLD,
    DOMINANCE_RATIO,
    REQUEST_TIMEOUT,
    HEADLESS,
    FIELD_MAP
)

# 🖼️ IMAGE EXTRACTION (ONLY <img>)
def extract_image_info(page_data):
    images = []

    for d in page_data:
        if d.get("tag") == "img" and d.get("src"):
            images.append(d["src"])

    images = list(dict.fromkeys(images))
    return {
        "image_count": len(images),
        "image_urls": images[:10]
    }


def choose_best_render(url):
    logger.info(f"Evaluating best render strategy for {url}")

    static_data = scrape_static(url)
    static_score = content_score(static_data)

    logger.info(f"Static score: {static_score}")

    if static_score >= STATIC_SCORE_THRESHOLD:
        logger.info("Static render selected")
        return static_data, "STATIC"

    dynamic_data = scrape_dynamic(url)
    dynamic_score = content_score(dynamic_data)

    logger.info(f"Dynamic score: {dynamic_score}")

    if dynamic_score > static_score * DOMINANCE_RATIO:
        logger.info("Dynamic render selected")
        return dynamic_data, "DYNAMIC"

    logger.info("Fallback to static render")
    return static_data, "STATIC"


def run():
    url = input("🌐 Enter website URL: ").strip()
    logger.info(f"Scraping started for URL: {url}")

    logger.info("Checking for public API")
    api_preview, api_endpoint = scrape_via_api(url, preview=True)

    # ✅ API PATH
    if api_preview:
        print("✅ API detected")
        logger.info(f"API detected at endpoint: {api_endpoint}")

        api_data, _ = scrape_via_api(url)

        export_txt([{
            "page_url": url,
            "content": {
                "text": str(api_data),
                "videos": []
            },
            "image_count": 0,
            "image_urls": []
        }])

        print("✅ Done (API-based)")
        logger.info("API-based scraping completed successfully")
        return

    print("❌ No API found. Using HTML rendering.")
    logger.info("No API found, switching to HTML scraping")

    raw_data, site_type = choose_best_render(url)
    print(f"🔍 Using {site_type} render")
    logger.info(f"Render mode selected: {site_type}")

    scrape_options = analyze_page_structure(raw_data)
    selected = ask_user_choice(scrape_options)
    internal_fields = [FIELD_MAP[s] for s in selected if s in FIELD_MAP]

    logger.info(f"User selected scrape fields: {selected}")

    crawl = input(f"🕷️ Crawl up to {MAX_PAGES} pages? (y/N): ").lower() == "y"
    logger.info(f"Crawling enabled: {crawl}")

    if crawl:
        urls = (
            crawl_site(url, MAX_PAGES)
            if site_type == "STATIC"
            else crawl_site_browser(url, MAX_PAGES)
        )
    else:
        urls = [url]

    logger.info(f"Total URLs to scrape: {len(urls)}")

    scraped_pages = []

    for i, page_url in enumerate(urls, 1):
        print(f"🔍 [{i}/{len(urls)}] {page_url}")
        logger.info(f"Scraping page {i}/{len(urls)}: {page_url}")

        data = (
            scrape_static(page_url, internal_fields)
            if site_type == "STATIC"
            else scrape_dynamic(page_url, internal_fields)
        )

        if data:
            scraped_pages.append({
                "page_url": page_url,
                "page_data": data
            })
            logger.info(f"Data extracted from {page_url}")
        else:
            logger.warning(f"No data extracted from {page_url}")

        time.sleep(0.5)  # polite crawling

    final_pages = []

    for page in scraped_pages:
        content = extract_meaningful_content(page["page_data"], page["page_url"])
        image_info = extract_image_info(page["page_data"])

        final_pages.append({
            "page_url": page["page_url"],
            "content": content,   # ✅ contains {text, videos}
            "image_count": image_info["image_count"],
            "image_urls": image_info["image_urls"]
        })

    export_txt(final_pages)
    print("✅ Done. Saved to output.txt")
    logger.info(f"Scraping completed successfully. Pages saved: {len(final_pages)}")


if __name__ == "__main__":
    run()
