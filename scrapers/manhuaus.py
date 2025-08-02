import requests
from bs4 import BeautifulSoup
from core.models import Chapter

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_chapters(manga_url: str) -> list[Chapter]:
    response = requests.get(manga_url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    chapters = []
    for a in soup.select(".wp-manga-chapter > a"):
        chapter_title = a.text.strip()
        chapter_url = a['href']
        number = chapter_title.split(" ")[-1]
        chapters.append(Chapter(number=number, title=chapter_title, url=chapter_url))

    # Ordem do site é decrescente, então invertemos
    return list(reversed(chapters))
