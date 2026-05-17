"""Exceções customizadas para o Scryll."""

class ScryllException(Exception):
    """Exceção base para todas as exceções do Scryll."""
    pass

class ScraperException(ScryllException):
    """Exceção base para erros de scraping."""
    pass

class NetworkException(ScraperException):
    """Erros relacionados a problemas de rede."""
    pass

class CloudflareException(NetworkException):
    """Site protegido por Cloudflare bloqueou o acesso."""
    def __init__(self, url: str, message: str = "Acesso bloqueado pelo Cloudflare"):
        self.url = url
        super().__init__(f"{message}: {url}")

class RateLimitException(NetworkException):
    """Rate limit excedido."""
    def __init__(self, site: str, retry_after: int = None):
        self.site = site
        self.retry_after = retry_after
        msg = f"Rate limit excedido para {site}"
        if retry_after:
            msg += f". Tente novamente em {retry_after}s"
        super().__init__(msg)

class ParsingException(ScraperException):
    """Erro ao fazer parsing do HTML."""
    def __init__(self, url: str, detail: str):
        self.url = url
        super().__init__(f"Erro ao parsear {url}: {detail}")

class ConfigurationException(ScryllException):
    """Erro de configuração."""
    pass

class ValidationException(ScryllException):
    """Erro de validação de dados."""
    pass

class DownloadException(ScryllException):
    """Erro durante download de imagens."""
    def __init__(self, url: str, reason: str):
        self.url = url
        super().__init__(f"Falha ao baixar {url}: {reason}")
