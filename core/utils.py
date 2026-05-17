import os
import time
from bs4 import BeautifulSoup
from loguru import logger


def sanitize_filename(text: str) -> str:
    return "".join(c for c in text if c.isalnum() or c in " ._-").strip()


def extract_image_urls(chapter_url: str) -> list:
    """Extract image URLs from chapter page using Cloudflare bypass."""
    from core import cf_bypass
    try:
        time.sleep(1)
        html = cf_bypass.fetch(chapter_url)
        soup = BeautifulSoup(html, "html.parser")
        imgs = soup.select(".reading-content img, .entry-content img, img.wp-manga-chapter-img, .page-break img")
        if not imgs:
            imgs = soup.find_all("img")
        urls = []
        for img in imgs:
            src = img.get("data-src") or img.get("src") or ""
            src = src.strip()
            if src and src.startswith("http"):
                urls.append(src)
        logger.info("{} imagens encontradas em {}", len(urls), chapter_url)
        return urls
    except Exception as e:
        logger.error("Erro ao extrair imagens de {}: {}", chapter_url, e)
        return []


def download_image(img_url: str, save_path: str, referer: str = ""):
    """Download image using Cloudflare bypass."""
    from core import cf_bypass
    try:
        time.sleep(0.3)
        content = cf_bypass.fetch_image(img_url, referer or img_url)
        with open(save_path, "wb") as f:
            f.write(content)
        logger.debug("Imagem salva: {}", save_path)
    except Exception as e:
        logger.error("Erro ao baixar imagem {}: {}", img_url, e)


def normalize_chapter_number(number) -> str:
    try:
        return str(float(number))
    except (ValueError, TypeError):
        return str(number).strip()
