import json
import sys
from scrapers import manhuaus, mangadex, comicpark, rfdragonscan, vortexscans
from core.downloader import download_new_chapters
from core.notifications import notify_telegram
from core.config import validate_config, validate_env_vars, validate_downloads_dir
from core.metrics import metrics_collector
from core.circuit_breaker import circuit_breaker
from core.exceptions import ScryllException, ConfigurationException
from loguru import logger
import os

# Configuração de logs estruturados
if not os.path.exists("logs"):
    os.makedirs("logs")

# Remove handler padrão
logger.remove()

# Handler para arquivo com rotação
logger.add(
    "logs/scryll.log",
    rotation="1 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    backtrace=True,
    diagnose=True
)

# Handler para console
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    colorize=True
)


SCRAPER_MAP = {
    "manhuaus": manhuaus.fetch_chapters,
    "mangadex": mangadex.fetch_chapters,
    "comicpark": comicpark.fetch_chapters,
    "rfdragon": rfdragonscan.fetch_chapters,
    "vortexscans": vortexscans.fetch_chapters
}

def main():
    logger.info("🚀 Iniciando Scryll...")
    
    try:
        # Valida ambiente
        validate_env_vars()
        validate_downloads_dir()
        
        # Carrega e valida configuração
        config = validate_config()
        
        logger.info(f"📚 Monitorando {len(config)} manga(s)")
        
    except (ConfigurationException, ScryllException) as e:
        logger.error(f"❌ Erro de configuração: {e}")
        notify_telegram(f"🔥 Scryll falhou ao iniciar:\n{e}")
        sys.exit(1)
    
    # Processa cada manga
    success_count = 0
    error_count = 0
    
    for item in config:
        name = item["name"]
        site = item["site"]
        url = item["url"]

        fetch_func = SCRAPER_MAP.get(site)
        if not fetch_func:
            logger.error(f"❌ Site não suportado: {site}")
            continue
        
        # Verifica circuit breaker
        if not circuit_breaker.is_available(site):
            logger.warning(f"⏭️ Pulando '{name}' ({site}): circuit breaker OPEN")
            continue

        try:
            logger.info(f"🔍 Buscando capítulos: {name} ({site})")
            
            # Registra tentativa
            metrics_collector.record_attempt(site)
            
            # Executa através do circuit breaker
            chapters = circuit_breaker.call(site, fetch_func, url)
            
            # Registra sucesso
            metrics_collector.record_success(site, len(chapters))
            
            download_new_chapters(name, site, chapters)
            success_count += 1
            
        except ScryllException as e:
            error_msg = f"Erro ao buscar '{name}' ({site}): {e}"
            logger.error(f"🔥 {error_msg}")
            metrics_collector.record_failure(site, type(e).__name__)
            notify_telegram(f"⚠️ {error_msg}")
            error_count += 1
            
        except Exception as e:
            error_msg = f"Erro inesperado em '{name}' ({site}): {e}"
            logger.exception(f"🔥 {error_msg}")
            metrics_collector.record_failure(site, "unknown")
            notify_telegram(f"🔥 {error_msg}")
            error_count += 1
    
    # Resumo final
    logger.info(f"✅ Execução concluída: {success_count} sucessos, {error_count} erros")
    metrics_collector.print_summary()
    
    if error_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
