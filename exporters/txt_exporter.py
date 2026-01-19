import os

def export_txt(pages, filename="output.txt"):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        for i, page in enumerate(pages, 1):
            f.write("=" * 80 + "\n")
            f.write(f"PAGE {i}\n")
            f.write("=" * 80 + "\n\n")

            f.write("PAGE URL:\n")
            f.write(page["page_url"] + "\n\n")

            # 📝 TEXT CONTENT
            f.write("PAGE CONTENT:\n")
            f.write("-" * 40 + "\n")

            content = page.get("content")
            if isinstance(content, dict):
                f.write(content.get("text") or "No meaningful content detected.")
            else:
                f.write(content or "No meaningful content detected.")

            f.write("\n\n")

            # 🖼 IMAGE DATA
            f.write("IMAGE DATA:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Image Count: {page['image_count']}\n")

            if page["image_urls"]:
                f.write("Image URLs:\n")
                for img in page["image_urls"]:
                    f.write(f"- {img}\n")
            else:
                f.write("No images found.\n")

            f.write("\n\n")

            # 🎥 VIDEO DATA (NEW)
            videos = []
            if isinstance(content, dict):
                videos = content.get("videos", [])

            f.write("VIDEO DATA:\n")
            f.write("-" * 40 + "\n")

            if videos:
                f.write(f"Video Count: {len(videos)}\n")
                for v in videos:
                    f.write(f"- {v}\n")
            else:
                f.write("No videos found.\n")

            f.write("\n\n")

    print(f"📄 Saved TXT output to {file_path}")
