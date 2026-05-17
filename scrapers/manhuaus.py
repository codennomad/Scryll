"""Scraper para ManhuaUS com bypass de Cloudflare via curl-cffi."""
from bs4 import BeautifulSoup
from core.models import Chapter
from core.retry import retry_with_backoff, rate_limiter
from core.exceptions import CloudflareException, ParsingException, NetworkException
from core import cf_bypass
from loguru import logger


@retry_with_backoff(max_attempts=2, initial_delay=10.0, exceptions=(NetworkException, CloudflareException))
def fetch_chapters(manga_url: str) -> list[Chapter]:
    """Busca capitulos usando curl-cffi (bypass de Cloudflare sem Selenium)."""
    rate_limiter.wait_if_needed("manhuaus", min_delay=5.0)
    logger.debug(f"Acessando {manga_url}...")

    try:
        html = cf_bypass.fetch(manga_url)
    except Exception as e:
        raise NetworkException(f"Falha ao buscar {manga_url}: {e}")

    if ("Just a moment" in html or
            ("cloudflare" in html.lower() and len(html) < 5000)):
        raise CloudflareException(manga_url)

    try:
        soup = BeautifulSoup(html, "html.parser")
        chapter_elements = soup.select(".wp-manga-chapter > a")

        if not chapter_elements:
            # Try alternate selectors
            chapter_elements = soup.select("li.wp-manga-chapter a")

        if not chapter_elements:
            raise ParsingException(manga_url, "Nenhum capitulo encontrado no HTML")

        chapters = []
        for a in chapter_elements:
            chapter_title = a.text.strip()
            chapter_url = a.get("href")
            if not chapter_url:
                continue
            number = chapter_title.split(" ")[-1]
            chapters.append(Chapter(number=number, title=chapter_title, url=chapter_url))

        return list(reversed(chapters))

    except ParsingException:
        raise
    except Exception as e:
        raise ParsingException(manga_url, str(e))