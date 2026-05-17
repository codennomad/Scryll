"""Scraper alternativo usando Selenium para sites com Cloudflare forte."""

import os
import time
from typing import Optional, List
from loguru import logger
from core.models import Chapter
from core.exceptions import CloudflareException, NetworkException

# Variável global para driver reutilizável
_driver = None
_driver_available = None

def is_selenium_available() -> bool:
    """Verifica se Selenium está disponível."""
    global _driver_available
    if _driver_available is not None:
        return _driver_available
    
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        _driver_available = True
        logger.info("✅ Selenium/Chrome disponível para bypass de Cloudflare")
        return True
    except ImportError:
        _driver_available = False
        logger.warning(
            "⚠️ undetected-chromedriver não disponível. "
            "Instale com: pip install undetected-chromedriver"
        )
        return False

def get_driver():
    """Obtém ou cria driver do Selenium."""
    global _driver
    
    if not is_selenium_available():
        raise ImportError("Selenium não está disponível")
    
    if _driver is not None:
        return _driver
    
    try:
        import undetected_chromedriver as uc
        from core.proxy_manager import proxy_manager
        
        logger.info("🌐 Iniciando navegador Chrome (pode demorar ~10s)...")
        
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')  # Modo headless
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Configura proxy se disponível
        if proxy_manager.has_proxies():
            proxy = proxy_manager.get_next_proxy()
            proxy_str = proxy.to_selenium_format()
            options.add_argument(f'--proxy-server={proxy_str}')
            logger.info(f"🔄 Chrome usando proxy: {proxy.http}")
        
        _driver = uc.Chrome(options=options, version_main=None)
        _driver.implicitly_wait(10)
        
        logger.success("✅ Navegador Chrome iniciado")
        return _driver
        
    except Exception as e:
        logger.error(f"❌ Falha ao iniciar Chrome: {e}")
        raise

def fetch_with_selenium(url: str, selector: str = ".wp-manga-chapter > a", timeout: int = 30) -> str:
    """
    Busca página usando Selenium para bypass de Cloudflare.
    
    Args:
        url: URL a buscar
        selector: Seletor CSS para aguardar
        timeout: Timeout em segundos
        
    Returns:
        HTML da página
    """
    try:
        driver = get_driver()
        
        logger.info(f"🌐 Carregando {url} com Selenium...")
        driver.get(url)
        
        # Aguarda Cloudflare resolver (se houver)
        logger.info("⏳ Aguardando resolução do Cloudflare (15s)...")
        time.sleep(15)
        
        # Verifica se há challenge do Cloudflare
        page_source = driver.page_source
        if 'Just a moment' in page_source or 'challenge' in page_source.lower():
            logger.info("⏳ Challenge detectado, aguardando mais 10s...")
            time.sleep(10)
            page_source = driver.page_source
        
        # Verifica se elementos esperados estão presentes
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            logger.success(f"✅ Página carregada com sucesso")
        except:
            logger.warning(f"⚠️ Seletor {selector} não encontrado, mas continuando...")
        
        return driver.page_source
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar com Selenium: {e}")
        raise NetworkException(f"Falha no Selenium: {e}")

def close_driver():
    """Fecha o driver do Selenium."""
    global _driver
    if _driver is not None:
        try:
            _driver.quit()
            logger.info("🔒 Navegador Chrome fechado")
        except:
            pass
        _driver = None

# Registra cleanup ao sair
import atexit
atexit.register(close_driver)
