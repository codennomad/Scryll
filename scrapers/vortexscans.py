import requests
from bs4 import BeautifulSoup
from core.models import Chapter

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def fetch_chapters(url: str) -> list[Chapter]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    chapters = []
    for a in soup.select(".wp-manga-chapter > a"):
        title = a.text.strip()
        chapter_url = a['href']
        number = title.split(" ")[-1]
        chapters.append(Chapter(number=number, title=title, url=chapter_url))

    return list(reversed(chapters))
