import os
import requests
from bs4 import BeautifulSoup
from loguru import logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def sanitize_filename(text: str) -> str:
    return "".join(c for c in text if c.isalnum() or c in " ._-").strip()

def extract_image_urls(chapter_url: str) -> list:
    try:
        response = requests.get(chapter_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        image_urls = []
        for img in soup.find_all("img"):
            if 'data-src' in img.attrs:
                image_urls.append(img['data-src'])
            elif 'src' in img.attrs:
                image_urls.append(img['src'])

        logger.info(f"🔗 {len(image_urls)} imagens encontradas em {chapter_url}")
        return image_urls
    except Exception as e:
        logger.error(f"❌ Erro ao extrair imagens de {chapter_url}: {e}")
        return []

def download_image(img_url: str, save_path: str):
    try:
        response = requests.get(img_url, headers=HEADERS)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        logger.debug(f"✅ Imagem salva: {save_path}")
    except Exception as e:
        logger.error(f"❌ Erro ao baixar imagem {img_url}: {e}")

def normalize_chapter_number(number) -> str:
    try:
        return str(float(number))
    except (ValueError, TypeError):
        return str(number).strip()
