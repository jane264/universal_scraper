import os
from openai import OpenAI

# Detect whether LLM is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_ENABLED = bool(OPENAI_API_KEY)

client = OpenAI(api_key=OPENAI_API_KEY) if LLM_ENABLED else None


def content_score(data):
    texts = [
        d.get("text", "").strip()
        for d in data
        if d.get("text")
    ]

    long_text = sum(len(t) for t in texts if len(t) > 40)
    unique_text = len(set(texts))
    list_items = sum(1 for d in data if d.get("tag") == "li")
    images = sum(1 for d in data if d.get("src"))

    return (
        long_text +
        unique_text * 50 +
        list_items * 30 +
        images * 10
    )


def analyze_page_structure(raw_data):
    has_text = any(d.get("text") for d in raw_data)
    has_links = any(d.get("href") for d in raw_data)
    has_images = any(d.get("src") for d in raw_data)

    options = []
    if has_text:
        options.append("Text Content")
    if has_links:
        options.append("Links")
    if has_images:
        options.append("Images")

    return options


def ask_user_choice(options):
    print("\nSelect what to scrape:")
    for i, o in enumerate(options, 1):
        print(f"{i}. {o}")
    print("Press Enter for ALL")

    raw = input("> ").strip()
    if not raw:
        return options

    selected = []
    for n in raw.split(","):
        if n.strip().isdigit():
            idx = int(n) - 1
            if 0 <= idx < len(options):
                selected.append(options[idx])

    return selected or options


# ─────────────────────────────────────────────
# 🧠 OPTIONAL LLM ENHANCER (GPT-4.1)
# ─────────────────────────────────────────────
def enhance_with_openai(text: str) -> str:
    """
    Uses GPT-4.1 ONLY if available.
    Otherwise returns text unchanged (rule-based fallback).
    """

    # 🚫 LLM disabled → pure rule-based pipeline
    if not LLM_ENABLED:
        return text

    if not text or len(text.strip()) < 50:
        return text

    # Safety cap (cost + latency)
    text = text[:6000]

    prompt = f"""
You are refining website text.

STRICT RULES:
- DO NOT add new information
- DO NOT remove factual content
- DO NOT hallucinate
- DO NOT mention scraping or AI
- Remove navigation, cookies, footers
- Improve clarity and readability
- Preserve original meaning
- Use clean paragraphs

TEXT:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You refine scraped web content without altering meaning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    except Exception:
        # 🔒 Absolute fallback — NEVER break scraper
        return text
