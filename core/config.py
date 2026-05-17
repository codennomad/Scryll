"""Validação de configurações."""

import os
import json
from typing import Any
from loguru import logger
from core.exceptions import ConfigurationException, ValidationException

SUPPORTED_SITES = ["manhuaus", "mangadex", "comicpark", "rfdragon", "vortexscans"]

def validate_env_vars():
    """Valida variáveis de ambiente necessárias."""
    warnings = []
    
    # Telegram é opcional mas útil
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        warnings.append("TELEGRAM_BOT_TOKEN não configurado - notificações desabilitadas")
    if not os.getenv("TELEGRAM_CHAT_ID"):
        warnings.append("TELEGRAM_CHAT_ID não configurado - notificações desabilitadas")
    
    if warnings:
        for warning in warnings:
            logger.warning(f"⚠️ {warning}")
    
    return len(warnings) == 0

def validate_config_item(item: dict, index: int) -> list[str]:
    """
    Valida um item de configuração.
    
    Returns:
        Lista de erros encontrados (vazia se válido)
    """
    errors = []
    
    # Valida campos obrigatórios
    if "name" not in item:
        errors.append(f"Item {index}: campo 'name' ausente")
    elif not isinstance(item["name"], str) or not item["name"].strip():
        errors.append(f"Item {index}: 'name' deve ser uma string não-vazia")
    
    if "site" not in item:
        errors.append(f"Item {index}: campo 'site' ausente")
    elif item["site"] not in SUPPORTED_SITES:
        errors.append(
            f"Item {index}: site '{item['site']}' não suportado. "
            f"Sites suportados: {', '.join(SUPPORTED_SITES)}"
        )
    
    if "url" not in item:
        errors.append(f"Item {index}: campo 'url' ausente")
    elif not isinstance(item["url"], str) or not item["url"].startswith("http"):
        errors.append(f"Item {index}: 'url' deve ser uma URL válida")
    
    return errors

def validate_config(config_path: str = "config.json") -> dict:
    """
    Valida o arquivo de configuração.
    
    Returns:
        Configuração validada
        
    Raises:
        ConfigurationException: Se houver erros críticos
    """
    # Verifica se arquivo existe
    if not os.path.exists(config_path):
        raise ConfigurationException(f"Arquivo {config_path} não encontrado")
    
    # Tenta carregar JSON
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigurationException(f"Erro ao parsear {config_path}: {e}")
    
    # Valida estrutura
    if not isinstance(config, list):
        raise ConfigurationException("config.json deve conter uma lista")
    
    if len(config) == 0:
        raise ConfigurationException("config.json está vazio")
    
    # Valida cada item
    all_errors = []
    for index, item in enumerate(config, start=1):
        if not isinstance(item, dict):
            all_errors.append(f"Item {index} deve ser um objeto")
            continue
        
        errors = validate_config_item(item, index)
        all_errors.extend(errors)
    
    # Se houver erros, lança exceção
    if all_errors:
        error_msg = "Erros na configuração:\n" + "\n".join(f"  - {e}" for e in all_errors)
        raise ValidationException(error_msg)
    
    logger.info(f"✅ Configuração validada: {len(config)} manga(s) configurado(s)")
    return config

def validate_downloads_dir(path: str = "downloads"):
    """Valida e cria diretório de downloads se necessário."""
    try:
        os.makedirs(path, exist_ok=True)
        # Testa permissão de escrita
        test_file = os.path.join(path, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        logger.debug(f"✅ Diretório de downloads OK: {path}")
    except Exception as e:
        raise ConfigurationException(f"Erro ao configurar diretório de downloads: {e}")
