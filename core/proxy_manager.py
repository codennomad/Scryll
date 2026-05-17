"""Gerenciador de proxies para bypass de bloqueios de IP."""

import os
import random
import requests
from typing import Optional, Dict, List
from loguru import logger
from dataclasses import dataclass

@dataclass
class ProxyConfig:
    """Configuração de um proxy."""
    http: str
    https: str
    username: Optional[str] = None
    password: Optional[str] = None
    
    def to_dict(self) -> Dict[str, str]:
        """Converte para dicionário compatível com requests."""
        if self.username and self.password:
            # Formato: http://user:pass@host:port
            http_proxy = self.http.replace('://', f'://{self.username}:{self.password}@')
            https_proxy = self.https.replace('://', f'://{self.username}:{self.password}@')
            return {
                'http': http_proxy,
                'https': https_proxy
            }
        return {
            'http': self.http,
            'https': self.https
        }
    
    def to_selenium_format(self) -> str:
        """Formato para Selenium."""
        # Extrai host:port do http proxy
        proxy_url = self.http
        if self.username and self.password:
            # Remove protocolo
            proxy = proxy_url.replace('http://', '').replace('https://', '')
            return f"{self.username}:{self.password}@{proxy}"
        return proxy_url.replace('http://', '').replace('https://', '')


class ProxyManager:
    """Gerencia lista de proxies com rotação."""
    
    def __init__(self):
        self.proxies: List[ProxyConfig] = []
        self.current_index = 0
        self._load_from_env()
    
    def _load_from_env(self):
        """Carrega proxies de variáveis de ambiente."""
        # Formato: PROXY_1=http://host:port|https://host:port
        # ou com auth: PROXY_1=http://host:port|https://host:port|user|pass
        
        proxy_http = os.getenv('PROXY_HTTP')
        proxy_https = os.getenv('PROXY_HTTPS')
        proxy_user = os.getenv('PROXY_USERNAME')
        proxy_pass = os.getenv('PROXY_PASSWORD')
        
        if proxy_http or proxy_https:
            proxy = ProxyConfig(
                http=proxy_http or proxy_https,
                https=proxy_https or proxy_http,
                username=proxy_user,
                password=proxy_pass
            )
            self.proxies.append(proxy)
            logger.info(f"✅ Proxy carregado do .env")
        
        # Suporta múltiplos proxies: PROXY_1, PROXY_2, etc
        i = 1
        while True:
            proxy_var = os.getenv(f'PROXY_{i}')
            if not proxy_var:
                break
            
            parts = proxy_var.split('|')
            if len(parts) >= 2:
                proxy = ProxyConfig(
                    http=parts[0],
                    https=parts[1],
                    username=parts[2] if len(parts) > 2 else None,
                    password=parts[3] if len(parts) > 3 else None
                )
                self.proxies.append(proxy)
                logger.info(f"✅ Proxy {i} carregado")
            i += 1
    
    def add_proxy(self, http: str, https: str = None, username: str = None, password: str = None):
        """Adiciona proxy manualmente."""
        proxy = ProxyConfig(
            http=http,
            https=https or http,
            username=username,
            password=password
        )
        self.proxies.append(proxy)
        logger.info(f"✅ Proxy adicionado: {http}")
    
    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Obtém próximo proxy da lista (rotação)."""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_random_proxy(self) -> Optional[ProxyConfig]:
        """Obtém proxy aleatório."""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def has_proxies(self) -> bool:
        """Verifica se há proxies configurados."""
        return len(self.proxies) > 0
    
    def test_proxy(self, proxy: ProxyConfig, test_url: str = "https://httpbin.org/ip") -> bool:
        """
        Testa se um proxy está funcionando.
        
        Returns:
            True se proxy funciona, False caso contrário
        """
        try:
            response = requests.get(
                test_url,
                proxies=proxy.to_dict(),
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"✅ Proxy funcionando: {proxy.http}")
                return True
            return False
        except Exception as e:
            logger.warning(f"⚠️ Proxy falhou no teste: {e}")
            return False
    
    def get_working_proxy(self) -> Optional[ProxyConfig]:
        """Retorna primeiro proxy que estiver funcionando."""
        for proxy in self.proxies:
            if self.test_proxy(proxy):
                return proxy
        return None


# Instância global
proxy_manager = ProxyManager()
