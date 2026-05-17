"""Testes para o módulo de configuração."""

import os
import json
import pytest
from core.config import validate_config_item, validate_config
from core.exceptions import ConfigurationException, ValidationException

def test_validate_config_item_valid():
    """Testa validação de item válido."""
    item = {
        "name": "Test Manga",
        "site": "manhuaus",
        "url": "https://example.com/manga"
    }
    errors = validate_config_item(item, 1)
    assert len(errors) == 0

def test_validate_config_item_missing_name():
    """Testa item sem nome."""
    item = {
        "site": "manhuaus",
        "url": "https://example.com/manga"
    }
    errors = validate_config_item(item, 1)
    assert len(errors) > 0
    assert any("name" in e.lower() for e in errors)

def test_validate_config_item_invalid_site():
    """Testa site não suportado."""
    item = {
        "name": "Test",
        "site": "invalid_site",
        "url": "https://example.com"
    }
    errors = validate_config_item(item, 1)
    assert len(errors) > 0
    assert any("suportado" in e.lower() for e in errors)

def test_validate_config_item_invalid_url():
    """Testa URL inválida."""
    item = {
        "name": "Test",
        "site": "manhuaus",
        "url": "not-a-url"
    }
    errors = validate_config_item(item, 1)
    assert len(errors) > 0
    assert any("url" in e.lower() for e in errors)

def test_validate_config_empty_file(tmp_path):
    """Testa arquivo de configuração vazio."""
    config_file = tmp_path / "config.json"
    config_file.write_text("[]")
    
    with pytest.raises(ConfigurationException, match="vazio"):
        validate_config(str(config_file))

def test_validate_config_invalid_json(tmp_path):
    """Testa JSON inválido."""
    config_file = tmp_path / "config.json"
    config_file.write_text("{ invalid json }")
    
    with pytest.raises(ConfigurationException, match="parsear"):
        validate_config(str(config_file))

def test_validate_config_valid(tmp_path):
    """Testa configuração válida."""
    config_file = tmp_path / "config.json"
    config = [
        {
            "name": "Test Manga 1",
            "site": "manhuaus",
            "url": "https://example.com/manga1"
        },
        {
            "name": "Test Manga 2",
            "site": "mangadex",
            "url": "https://example.com/manga2"
        }
    ]
    config_file.write_text(json.dumps(config))
    
    result = validate_config(str(config_file))
    assert len(result) == 2
    assert result[0]["name"] == "Test Manga 1"
