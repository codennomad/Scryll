"""Utilitário para retry com backoff exponencial."""

import time
import functools
from typing import Callable, TypeVar, Any
from loguru import logger
from core.exceptions import NetworkException, CloudflareException

T = TypeVar('T')

def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (NetworkException, Exception)
):
    """
    Decorator para retry com backoff exponencial.
    
    Args:
        max_attempts: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        backoff_factor: Fator de multiplicação do delay
        max_delay: Delay máximo em segundos
        exceptions: Tupla de exceções que devem triggerar retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except CloudflareException as e:
                    # Cloudflare não adianta retry imediato
                    logger.warning(f"🛡️ Cloudflare detectado em {e.url}, abortando retries")
                    raise
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(f"❌ Falha após {max_attempts} tentativas: {func.__name__}")
                        raise
                    
                    logger.warning(
                        f"⚠️ Tentativa {attempt}/{max_attempts} falhou para {func.__name__}: {str(e)[:100]}"
                    )
                    logger.info(f"⏳ Aguardando {delay:.1f}s antes de tentar novamente...")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            raise last_exception
        return wrapper
    return decorator


class RateLimiter:
    """Rate limiter simples baseado em tempo."""
    
    def __init__(self):
        self._last_request = {}
    
    def wait_if_needed(self, site: str, min_delay: float = 2.0):
        """
        Aguarda se necessário para respeitar rate limit.
        
        Args:
            site: Nome do site
            min_delay: Delay mínimo entre requisições em segundos
        """
        now = time.time()
        last = self._last_request.get(site, 0)
        elapsed = now - last
        
        if elapsed < min_delay:
            wait_time = min_delay - elapsed
            logger.debug(f"⏱️ Rate limit: aguardando {wait_time:.1f}s para {site}")
            time.sleep(wait_time)
        
        self._last_request[site] = time.time()
    
    def reset(self, site: str = None):
        """Reseta o rate limiter para um site específico ou todos."""
        if site:
            self._last_request.pop(site, None)
        else:
            self._last_request.clear()


# Instância global do rate limiter
rate_limiter = RateLimiter()
