from typing import List, Dict
from collections import Counter
from urllib.parse import urljoin

# ✅ LLM AUTO-SWITCH IMPORTS (NEW)
from core.utils import enhance_with_openai, LLM_ENABLED
from core.logger import logger

MIN_TEXT_LENGTH = 40

JUNK_KEYWORDS = [
    "cookie", "privacy", "terms", "sign in", "sign up",
    "login", "register", "copyright", "all rights reserved"
]

VIDEO_EXTENSIONS = (".mp4", ".webm", ".ogg", ".m3u8")


def extract_meaningful_content(page_data: List[dict], base_url: str) -> Dict:
    texts = []
    videos = []

    raw_texts = [
        d.get("text", "").strip()
        for d in page_data
        if d.get("text")
    ]
    freq = Counter(raw_texts)

    for d in page_data:
        tag = (d.get("tag") or "").lower()
        text = d.get("text", "")
        src = d.get("src")
        href = d.get("href")

        # 🎥 VIDEO EXTRACTION (SAFE & ABSOLUTE URLs)
        if tag in ("video", "source") and src:
            if isinstance(src, str) and src.lower().endswith(VIDEO_EXTENSIONS):
                videos.append(urljoin(base_url, src))
            continue

        # 🎥 <a href="video.mp4">
        if tag == "a" and isinstance(href, str):
            if href.lower().endswith(VIDEO_EXTENSIONS):
                videos.append(urljoin(base_url, href))
            continue

        if not text:
            continue

        text = text.strip()
        lowered = text.lower()

        if any(j in lowered for j in JUNK_KEYWORDS):
            continue

        if len(text) < MIN_TEXT_LENGTH:
            if freq[text] < 2:
                continue

        if tag == "a" and len(text.split()) < 3:
            continue

        texts.append(text)

    unique_texts = list(dict.fromkeys(texts))

    # ─────────────────────────────────────────
    # 🧠 AUTO LLM SWITCH (ONLY CHANGE)
    # ─────────────────────────────────────────
    final_text = "\n\n".join(unique_texts)

    if LLM_ENABLED:
        logger.info("🧠 LLM enhancement enabled")
        final_text = enhance_with_openai(final_text)
    else:
        logger.info("⚙️ LLM not available, using rule-based text")

    return {
        "text": final_text,
        "videos": list(dict.fromkeys(videos))
    }
