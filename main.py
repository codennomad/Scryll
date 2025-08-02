import json
from scrapers import manhuaus, mangadex, comicpark, rfdragonscan, vortexscans
from core.downloader import download_new_chapters
from core.notifications import notify_telegram
from loguru import logger
import os

if not os.path.exists("logs"):
    os.makedirs("logs")
    
logger.add("logs/scryll.log", rotation="1 MB", retention="7 days", level="INFO")


SCRAPER_MAP = {
    "manhuaus": manhuaus.fetch_chapters,
    "mangadex": mangadex.fetch_chapters,
    "comicpark": comicpark.fetch_chapters,
    "rfdragon": rfdragonscan.fetch_chapters,
    "vortexscans": vortexscans.fetch_chapters
}

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    config = load_config()
    
    for item in config:
        name = item["name"]
        site = item["site"]
        url = item["url"]

        fetch_func = SCRAPER_MAP.get(site)
        if not fetch_func:
            logger.error(f"❌ Site não suportado: {site}")
            continue

        try:
            logger.info(f"🔍 Buscando capítulos: {name} ({site})")
            chapters = fetch_func(url)
            download_new_chapters(name, site, chapters)
        except Exception as e:
            error_msg = f"🔥 Erro ao buscar '{name}' ({site}): {e}"
            logger.exception(error_msg)
            notify_telegram(error_msg)

if __name__ == "__main__":
    main()
