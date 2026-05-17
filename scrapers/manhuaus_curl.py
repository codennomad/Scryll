import subprocess
from bs4 import BeautifulSoup
from core.models import Chapter
from core.retry import retry_with_backoff, rate_limiter
from core.exceptions import CloudflareException, ParsingException, NetworkException
from loguru import logger
import re

def fetch_with_curl(url: str) -> str:
    """Busca HTML usando curl (funciona com VPN para bypass Cloudflare)"""
    cmd = [
        'curl', '-sL', url,
        '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        '-H', 'Accept-Language: en-US,en;q=0.5',
        '-H', 'Referer: https://manhuaus.com/',
        '--compressed',
        '--max-time', '30'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    
    if result.returncode != 0:
        raise NetworkException(f"curl falhou com código {result.returncode}")
    
    html = result.stdout
    
    # Verifica se é challenge do Cloudflare
    if "Just a moment" in html or "cf_chl_opt" in html:
        raise CloudflareException(f"Cloudflare challenge em {url}")
    
    return html

@retry_with_backoff(max_attempts=2, initial_delay=3.0, exceptions=(NetworkException,))
def fetch_chapters(manga_url: str) -> list[Chapter]:
    """
    Busca capítulos de um mangá no ManhuaUS usando curl via VPN.
    
    Raises:
        CloudflareException: Se bloqueado pelo Cloudflare
        NetworkException: Erro de rede
        ParsingException: Erro ao parsear HTML
    """
    rate_limiter.wait_if_needed('manhuaus')
    
    logger.info(f"🔍 Buscando capítulos via curl+VPN: {manga_url}")
    
    try:
        html = fetch_with_curl(manga_url)
        logger.debug(f"✅ HTML baixado: {len(html)} caracteres")
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Busca capítulos com seletor padrão do ManhuaUS
        chapter_elements = soup.select('.wp-manga-chapter > a')
        
        if not chapter_elements:
            logger.warning(f"⚠️ Nenhum capítulo encontrado com seletor .wp-manga-chapter > a")
            raise ParsingException(f"Nenhum capítulo encontrado em {manga_url}")
        
        chapters = []
        for elem in chapter_elements:
            try:
                url = elem.get('href', '').strip()
                title = elem.get_text(strip=True)
                
                if not url or not title:
                    continue
                
                # Extrai número do capítulo
                match = re.search(r'chapter[- ]?(\d+(?:\.\d+)?)', title, re.I)
                number = float(match.group(1)) if match else 0
                
                chapters.append(Chapter(
                    number=number,
                    title=title,
                    url=url
                ))
            except Exception as e:
                logger.debug(f"Erro ao parsear capítulo: {e}")
                continue
        
        logger.success(f"✅ Encontrados {len(chapters)} capítulos")
        return sorted(chapters, key=lambda c: c.number)
        
    except subprocess.TimeoutExpired:
        raise NetworkException(f"Timeout ao buscar {manga_url}")
    except CloudflareException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise ParsingException(f"Erro ao parsear {manga_url}: {e}")
