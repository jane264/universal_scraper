import csv

# Used only when exporting generic scraped data
FIELD_MAP = {
    "Text Content": "text",
    "Links": "href",
    "Images": "src"
}


def export_csv(data, selected=None, filename="output.csv"):
    """
    Export data to CSV.

    CASE 1 (selected=None):
        Structured data
        Example:
        [
            {"page_url": "...", "summary": "...", "images": "..."},
            ...
        ]

    CASE 2 (selected=[...]):
        Generic scraped data (text / links / images)
    """

    if not data:
        print("⚠️ No data to export.")
        return

    # ─────────────────────────────
    # CASE 1: STRUCTURED DATA (LLM output, API data, etc.)
    # ─────────────────────────────
    if selected is None:
        headers = list(data[0].keys())

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

            for row in data:
                # Ensure all headers exist
                safe_row = {h: row.get(h, "") for h in headers}
                writer.writerow(safe_row)

        print(f"📄 Exported {len(data)} rows to {filename}")
        return

    # ─────────────────────────────
    # CASE 2: GENERIC SCRAPED DATA
    # ─────────────────────────────
    rows = []

    for d in data:
        row = {}

        for option in selected:
            key = FIELD_MAP.get(option)
            value = d.get(key)

            if isinstance(value, str):
                row[option] = value.strip()
            else:
                row[option] = ""

        # Keep row only if something exists
        if any(row.values()):
            rows.append(row)

    if not rows:
        print("⚠️ Data exists but no selected fields matched.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"📄 Exported {len(rows)} rows to {filename}")
