"""Download official manga covers from manhuaus.com and save to downloads/<name>/cover.webp"""
import sys
import json
import os
import time
from pathlib import Path

sys.path.insert(0, '/home/kaspian/Scryll')

from loguru import logger
from core import cf_bypass
from bs4 import BeautifulSoup

DOWNLOADS_DIR = Path('/home/kaspian/Scryll/downloads')
CONFIG_PATH   = Path('/home/kaspian/Scryll/config.json')

COVER_SELECTORS = [
    '.summary_image img',
    '.summary-image img',
    '.tab-summary .summary_image img',
    '.post-thumbnail img',
    '.manga-thumbnail img',
]


def extract_cover_url(html: str) -> str | None:
    soup = BeautifulSoup(html, 'html.parser')
    for selector in COVER_SELECTORS:
        el = soup.select_one(selector)
        if el:
            src = el.get('data-src') or el.get('data-lazy-src') or el.get('src') or ''
            src = src.strip()
            if src.startswith('http') and any(ext in src for ext in ['.webp', '.jpg', '.jpeg', '.png']):
                logger.info('Cover found via "{}": {}', selector, src[:80])
                return src
    return None


def download_cover(manga_name: str, manga_url: str) -> bool:
    series_dir = DOWNLOADS_DIR / manga_name
    if not series_dir.exists():
        logger.warning('No download dir for "{}". Skipping.', manga_name)
        return False

    # Check if cover already exists
    for ext in ['webp', 'jpg', 'jpeg', 'png']:
        if (series_dir / f'cover.{ext}').exists():
            logger.info('Cover already exists for "{}"', manga_name)
            return True

    logger.info('Fetching cover for "{}" from {}', manga_name, manga_url)
    try:
        html = cf_bypass.fetch(manga_url)
        cover_url = extract_cover_url(html)
        if not cover_url:
            logger.warning('No cover URL found for "{}"', manga_name)
            return False

        ext = cover_url.split('.')[-1].split('?')[0].lower()
        if ext not in ('webp', 'jpg', 'jpeg', 'png'):
            ext = 'jpg'

        logger.info('Downloading cover: {}', cover_url[:80])
        img_bytes = cf_bypass.fetch_image(cover_url, manga_url)
        cover_path = series_dir / f'cover.{ext}'
        cover_path.write_bytes(img_bytes)
        logger.success('Cover saved: {} ({} KB)', cover_path.name, len(img_bytes) // 1024)
        return True

    except Exception as e:
        logger.error('Failed to download cover for "{}": {}', manga_name, e)
        return False


def main():
    config = json.loads(CONFIG_PATH.read_text())
    logger.info('Downloading covers for {} manga(s)...', len(config))
    ok = 0
    fail = 0
    for item in config:
        name = item['name']
        url  = item['url']
        if item.get('site') != 'manhuaus':
            logger.info('Skipping "{}" (site: {})', name, item.get('site'))
            continue
        success = download_cover(name, url)
        if success:
            ok += 1
        else:
            fail += 1
        time.sleep(2)

    logger.info('Done: {} covers downloaded, {} failed', ok, fail)


if __name__ == '__main__':
    main()
