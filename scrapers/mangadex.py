import requests
from core.models import Chapter
from loguru import logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

BASE_URL = "https://api.mangadex.org"

def get_title_id(manga_url: str) -> str:
    import re
    match = re.search(r'[0-9a-fA-F-]{36}', manga_url)
    if not match:
        raise ValueError(f"URL inválida: não contém UUID → {manga_url}")
    return match.group(0)

def try_fetch(manga_id: str, lang: str) -> list[dict]:
    params = {
        "manga": manga_id,
        "translatedLanguage[]": [lang],
        "order[chapter]": "asc",
        "limit": 500
    }

    response = requests.get(f"{BASE_URL}/chapter", params=params, headers=HEADERS)
    
    if response.status_code == 400:
        return []  # sem capítulos no idioma
    response.raise_for_status()
    
    return response.json().get("data", [])

def fetch_chapters(manga_url: str) -> list[Chapter]:
    manga_id = get_title_id(manga_url)

    # tenta pt-br primeiro
    chapter_data = try_fetch(manga_id, "pt-br")
    idioma_usado = "pt-br"

    # se falhar, tenta en
    if not chapter_data:
        chapter_data = try_fetch(manga_id, "en")
        idioma_usado = "en" if chapter_data else None

    # se nenhum idioma tiver capítulos
    if not chapter_data:
        logger.error(f"📛 Nenhum capítulo encontrado para '{manga_url}' em pt-br ou en.")
        return []

    chapters = []
    for chapter in chapter_data:
        attr = chapter["attributes"]
        chapter_number = attr.get("chapter") or "?"
        title = attr.get("title") or ""
        chapter_id = chapter["id"]
        full_title = f"Chapter {chapter_number} - {title}".strip(" -")

        chapters.append(Chapter(
            number=chapter_number,
            title=full_title,
            url=f"https://mangadex.org/chapter/{chapter_id}"
        ))

    logger.info(f"✅ Capítulos encontrados para {manga_url} ({idioma_usado}) → {len(chapters)} capítulos")
    return chapters
