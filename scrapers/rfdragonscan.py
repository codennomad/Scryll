import requests
from bs4 import BeautifulSoup
from core.models import Chapter

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

BASE_URL = "https://rfdragonscan.com"

def fetch_chapters(manga_url: str) -> list[Chapter]:
    response = requests.get(manga_url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    
    # No RFDragonScan os capítulos geralmente ficam em: div.listing-chapters > ul > li > a
    chapter_links = soup.select("div.listing-chapters ul li a")
    
    chapters = []
    for link in reversed(chapter_links):
        url = link['href']
        title = link.get_text(strip=True)
        
        # Extrair número do capítulo a partir da URL ou do texto
        number = url.rstrip('/').split('/')[-1]  # último segmento da URL
        
        chapters.append(Chapter(
            number=number,
            title=title,
            url=url
        ))

    return chapters
