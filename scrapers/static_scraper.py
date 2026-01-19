import requests
from bs4 import BeautifulSoup

def scrape_static(url, fields=None, preview=False):
    r = requests.get(url, timeout=10)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "lxml")

    data = []
    for tag in soup.find_all(["h1", "h2", "p", "a", "img", "li", "video", "source"]):
        src = (
            tag.get("src")
            or tag.get("data-src")
            or tag.get("data-lazy")
            or tag.get("srcset")
        )

        data.append({
            "tag": tag.name.lower(),
            "text": tag.get_text(strip=True),
            "href": tag.get("href"),
            "src": src
        })

    if preview:
        return data[:10]

    # 🔒 DO NOT DROP tag/src EVER
    if fields:
        return [{
            "tag": d.get("tag"),
            "text": d.get("text") if "text" in fields else None,
            "href": d.get("href"),
            "src": d.get("src")
        } for d in data]

    return data
