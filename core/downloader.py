import os
import json
import requests
from loguru import logger
from core.notifications import notify_telegram
from core.utils import sanitize_filename, extract_image_urls, download_image, normalize_chapter_number

DOWNLOADS_PATH = "downloaded.json"
CHAPTERS_DIR = "downloads"

os.makedirs(CHAPTERS_DIR, exist_ok=True)

def load_downloaded() -> dict:
    if not os.path.exists(DOWNLOADS_PATH):
        return {}
    with open(DOWNLOADS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_downloaded(data: dict):
    with open(DOWNLOADS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def download_new_chapters(title: str, site: str, chapters: list):
    downloaded = load_downloaded()
    site_data = downloaded.get(site, {})
    downloaded_numbers = {normalize_chapter_number(n) for n in site_data.get(title, [])}

    new_chapters = [c for c in chapters if normalize_chapter_number(c.number) not in downloaded_numbers]

    if not new_chapters:
        logger.info(f"✅ Nenhum capítulo novo de '{title}' ({site}).")
        return

    for chapter in new_chapters:
        try:
            folder = os.path.join(CHAPTERS_DIR, sanitize_filename(title), f"chapter_{chapter.number}")
            os.makedirs(folder, exist_ok=True)

            image_urls = extract_image_urls(chapter.url)

            if not image_urls:
                logger.warning(f"⚠️ Nenhuma imagem encontrada em {chapter.url}")
                continue

            for idx, img_url in enumerate(image_urls, start=1):
                ext = os.path.splitext(img_url)[1].split("?")[0].lower()
                if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                    ext = ".jpg"  # Padrão
                save_path = os.path.join(folder, f"{idx:03d}{ext}")
                download_image(img_url, save_path)

            logger.success(f"📥 Novo capítulo baixado: {title} {chapter.title} ({chapter.url})")
            notify_telegram(f"📚 *Novo capítulo disponível!*\n*{title}*\n{chapter.title}\n🔗 {chapter.url}")

            # Atualiza lista de capítulos baixados
            site_data.setdefault(title, []).append(chapter.number)
            downloaded[site] = site_data

        except Exception as e:
            logger.error(f"❌ Erro ao baixar {title} {chapter.title}: {e}")

    # Remove duplicados e salva
    for key in downloaded.get(site, {}):
        downloaded[site][key] = sorted(
            {normalize_chapter_number(n) for n in downloaded[site][key]},
            key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else x
        )

    save_downloaded(downloaded)
