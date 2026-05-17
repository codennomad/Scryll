"""Testes para utilitários."""

import pytest
from core.utils import sanitize_filename, normalize_chapter_number

def test_sanitize_filename():
    """Testa sanitização de nomes de arquivo."""
    assert sanitize_filename("Normal Name") == "Normal Name"
    assert sanitize_filename("Name/with\\slashes") == "Namewithslashes"
    assert sanitize_filename("Name:with*special?chars") == "Namewithspecialchars"
    assert sanitize_filename("  Spaces  ") == "Spaces"

def test_normalize_chapter_number():
    """Testa normalização de números de capítulo."""
    assert normalize_chapter_number("42") == "42.0"
    assert normalize_chapter_number("42.5") == "42.5"
    assert normalize_chapter_number(42) == "42.0"
    assert normalize_chapter_number("special") == "special"
