import requests
import re
from urllib.parse import urljoin

COMMON_API_PATHS = [
    "/api",
    "/api/v1",
    "/api/v2",
    "/wp-json",
    "/graphql",
    "/v1",
    "/v2"
]

def is_json_response(resp):
    ct = resp.headers.get("Content-Type", "").lower()
    return "application/json" in ct

def try_direct_api(url):
    try:
        r = requests.get(url, timeout=15)
        r.encoding = "utf-8"
    except Exception:
        return None, None

    if r.status_code == 200 and is_json_response(r):
        try:
            return url, r.json()
        except Exception:
            return None, None

    return None, None

def try_common_paths(base_url):
    for path in COMMON_API_PATHS:
        endpoint = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        try:
            r = requests.get(endpoint, timeout=15)
            r.encoding = "utf-8"
        except Exception:
            continue

        if r.status_code == 200 and is_json_response(r):
            try:
                return endpoint, r.json()
            except Exception:
                continue

    return None, None

def discover_api_from_html(base_url):
    try:
        r = requests.get(base_url, timeout=15)
        r.encoding = r.apparent_encoding or "utf-8"
    except Exception:
        return None, None

    matches = re.findall(
        r'https?://[^"\']+/(api|wp-json|graphql|v1|v2)[^"\']*',
        r.text,
        re.IGNORECASE
    )

    for url in set(matches):
        try:
            r2 = requests.get(url, timeout=15)
            r2.encoding = "utf-8"
        except Exception:
            continue

        if r2.status_code == 200 and is_json_response(r2):
            try:
                return url, r2.json()
            except Exception:
                continue

    return None, None

def scrape_via_api(url, fields=None, preview=False):
    """
    ALWAYS returns: (records, api_endpoint)
    """
    endpoint, data = try_direct_api(url)

    if not data:
        endpoint, data = try_common_paths(url)

    if not data:
        endpoint, data = discover_api_from_html(url)

    if not data:
        return [], None   # 🔑 CRITICAL

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and "results" in data:
        records = data["results"]
    elif isinstance(data, dict):
        records = [data]
    else:
        return [], None

    if preview:
        return records[:5], endpoint

    if fields:
        records = [{k: rec.get(k) for k in fields} for rec in records]

    return records, endpoint
