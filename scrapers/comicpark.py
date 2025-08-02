import requests
from bs4 import BeautifulSoup
import re
from core.models import Chapter

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def extract_number(title: str) -> str:
    match = re.search(r'\d+(\.\d+)?', title)
    return match.group(0) if match else "?"

def fetch_chapters(manga_url: str) -> list[Chapter]:
    response = requests.get(manga_url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    chapter_elements = soup.select("ul.chapter-list li a")

    chapters = []
    for link in reversed(chapter_elements):
        url = "https://comicpark.org" + link["href"]
        title = link.get_text(strip=True)
        number = extract_number(title)

        chapters.append(Chapter(number=number, title=title, url=url))

    return chapters
