from playwright.sync_api import sync_playwright

def scrape_dynamic(url, fields=None, preview=False):
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        page.evaluate("""
        () => new Promise(resolve => {
            let y = 0;
            const step = 600;
            const timer = setInterval(() => {
                window.scrollBy(0, step);
                y += step;
                if (y > document.body.scrollHeight) {
                    clearInterval(timer);
                    resolve();
                }
            }, 250);
        })
        """)
        page.wait_for_timeout(2000)

        elements = page.query_selector_all("body *")

        for el in elements:
            try:
                tag_name = el.evaluate("e => e.tagName.toLowerCase()")

                inner = el.inner_text() or ""
                text_content = el.evaluate("e => e.textContent") or ""
                aria = el.get_attribute("aria-label") or ""
                title = el.get_attribute("title") or ""

                src = (
                    el.get_attribute("src")
                    or el.get_attribute("data-src")
                    or el.get_attribute("srcset")
                )

            except Exception:
                continue

            combined = " ".join([
                inner.strip(),
                text_content.strip(),
                aria.strip(),
                title.strip()
            ]).strip()

            if not combined and tag_name not in ("video", "source"):
                continue

            data.append({
                "tag": tag_name,
                "text": combined,
                "href": el.get_attribute("href"),
                "src": src
            })

        browser.close()

    if preview:
        return data[:10]

    # 🔒 PRESERVE STRUCTURAL DATA
    if fields:
        return [{
            "tag": d.get("tag"),
            "text": d.get("text") if "text" in fields else None,
            "href": d.get("href"),
            "src": d.get("src")
        } for d in data]

    return data
