"""Sistema de métricas e monitoramento."""

import json
import os
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass, field, asdict
from loguru import logger

@dataclass
class ScraperMetrics:
    """Métricas de um scraper específico."""
    site: str
    total_attempts: int = 0
    successful: int = 0
    failed: int = 0
    cloudflare_blocks: int = 0
    network_errors: int = 0
    parsing_errors: int = 0
    chapters_found: int = 0
    chapters_downloaded: int = 0
    last_success: str = None
    last_failure: str = None
    consecutive_failures: int = 0
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso em porcentagem."""
        if self.total_attempts == 0:
            return 0.0
        return (self.successful / self.total_attempts) * 100
    
    @property
    def is_healthy(self) -> bool:
        """Verifica se o scraper está saudável."""
        return self.consecutive_failures < 3


class MetricsCollector:
    """Coleta e persiste métricas do sistema."""
    
    def __init__(self, metrics_file: str = "metrics.json"):
        self.metrics_file = metrics_file
        self.metrics: Dict[str, ScraperMetrics] = {}
        self._load_metrics()
    
    def _load_metrics(self):
        """Carrega métricas do arquivo."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for site, metrics_dict in data.items():
                        self.metrics[site] = ScraperMetrics(**metrics_dict)
                logger.debug(f"📊 Métricas carregadas de {self.metrics_file}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar métricas: {e}")
    
    def _save_metrics(self):
        """Salva métricas no arquivo."""
        try:
            data = {site: asdict(metrics) for site, metrics in self.metrics.items()}
            with open(self.metrics_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar métricas: {e}")
    
    def get_metrics(self, site: str) -> ScraperMetrics:
        """Obtém métricas de um site."""
        if site not in self.metrics:
            self.metrics[site] = ScraperMetrics(site=site)
        return self.metrics[site]
    
    def record_attempt(self, site: str):
        """Registra uma tentativa de scraping."""
        metrics = self.get_metrics(site)
        metrics.total_attempts += 1
        self._save_metrics()
    
    def record_success(self, site: str, chapters_found: int = 0):
        """Registra um scraping bem-sucedido."""
        metrics = self.get_metrics(site)
        metrics.successful += 1
        metrics.chapters_found += chapters_found
        metrics.last_success = datetime.now().isoformat()
        metrics.consecutive_failures = 0
        self._save_metrics()
        logger.info(f"✅ {site}: {chapters_found} capítulos encontrados")
    
    def record_failure(self, site: str, error_type: str = "unknown"):
        """Registra uma falha de scraping."""
        metrics = self.get_metrics(site)
        metrics.failed += 1
        metrics.last_failure = datetime.now().isoformat()
        metrics.consecutive_failures += 1
        
        # Categoriza erro
        if "cloudflare" in error_type.lower():
            metrics.cloudflare_blocks += 1
        elif "network" in error_type.lower():
            metrics.network_errors += 1
        elif "parsing" in error_type.lower():
            metrics.parsing_errors += 1
        
        self._save_metrics()
        
        # Alerta se muitas falhas consecutivas
        if metrics.consecutive_failures >= 3:
            logger.warning(
                f"⚠️ {site}: {metrics.consecutive_failures} falhas consecutivas"
            )
    
    def record_download(self, site: str, chapters_count: int = 1):
        """Registra capítulos baixados."""
        metrics = self.get_metrics(site)
        metrics.chapters_downloaded += chapters_count
        self._save_metrics()
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo geral das métricas."""
        total_attempts = sum(m.total_attempts for m in self.metrics.values())
        total_successful = sum(m.successful for m in self.metrics.values())
        total_chapters = sum(m.chapters_downloaded for m in self.metrics.values())
        
        return {
            "total_sites": len(self.metrics),
            "total_attempts": total_attempts,
            "total_successful": total_successful,
            "total_chapters_downloaded": total_chapters,
            "success_rate": (total_successful / total_attempts * 100) if total_attempts > 0 else 0,
            "unhealthy_sites": [
                site for site, m in self.metrics.items() if not m.is_healthy
            ]
        }
    
    def print_summary(self):
        """Imprime resumo das métricas."""
        summary = self.get_summary()
        logger.info("📊 === RESUMO DE MÉTRICAS ===")
        logger.info(f"Sites monitorados: {summary['total_sites']}")
        logger.info(f"Taxa de sucesso geral: {summary['success_rate']:.1f}%")
        logger.info(f"Capítulos baixados: {summary['total_chapters_downloaded']}")
        
        if summary['unhealthy_sites']:
            logger.warning(f"Sites com problemas: {', '.join(summary['unhealthy_sites'])}")
        
        # Detalha cada site
        for site, metrics in sorted(self.metrics.items()):
            status = "✅" if metrics.is_healthy else "❌"
            logger.info(
                f"{status} {site}: {metrics.success_rate:.1f}% sucesso, "
                f"{metrics.chapters_downloaded} baixados, "
                f"{metrics.consecutive_failures} falhas consecutivas"
            )


# Instância global
metrics_collector = MetricsCollector()
