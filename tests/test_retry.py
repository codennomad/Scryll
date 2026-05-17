"""Testes para o sistema de retry."""

import pytest
from unittest.mock import Mock
from core.retry import retry_with_backoff, RateLimiter
from core.exceptions import NetworkException, CloudflareException
import time

def test_retry_success_on_first_attempt():
    """Testa função que sucede na primeira tentativa."""
    mock_func = Mock(return_value="success")
    decorated = retry_with_backoff(max_attempts=3)(mock_func)
    
    result = decorated()
    
    assert result == "success"
    assert mock_func.call_count == 1

def test_retry_success_after_failures():
    """Testa função que sucede após falhas."""
    mock_func = Mock(side_effect=[NetworkException("fail"), NetworkException("fail"), "success"])
    decorated = retry_with_backoff(max_attempts=3, initial_delay=0.1)(mock_func)
    
    result = decorated()
    
    assert result == "success"
    assert mock_func.call_count == 3

def test_retry_max_attempts_exceeded():
    """Testa exceção quando máximo de tentativas é excedido."""
    mock_func = Mock(side_effect=NetworkException("persistent error"))
    decorated = retry_with_backoff(max_attempts=3, initial_delay=0.1)(mock_func)
    
    with pytest.raises(NetworkException):
        decorated()
    
    assert mock_func.call_count == 3

def test_retry_cloudflare_no_retry():
    """Testa que CloudflareException não faz retry."""
    mock_func = Mock(side_effect=CloudflareException("https://example.com"))
    decorated = retry_with_backoff(max_attempts=3)(mock_func)
    
    with pytest.raises(CloudflareException):
        decorated()
    
    # Deve falhar imediatamente, sem retry
    assert mock_func.call_count == 1

def test_rate_limiter():
    """Testa rate limiter."""
    limiter = RateLimiter()
    
    # Primeira requisição deve ser instantânea
    start = time.time()
    limiter.wait_if_needed("test", min_delay=0.2)
    elapsed1 = time.time() - start
    assert elapsed1 < 0.1
    
    # Segunda requisição deve esperar
    start = time.time()
    limiter.wait_if_needed("test", min_delay=0.2)
    elapsed2 = time.time() - start
    assert elapsed2 >= 0.15  # Pelo menos 0.2s mas com margem

def test_rate_limiter_different_sites():
    """Testa que sites diferentes não interferem."""
    limiter = RateLimiter()
    
    limiter.wait_if_needed("site1", min_delay=1.0)
    
    # Requisição para site2 deve ser instantânea
    start = time.time()
    limiter.wait_if_needed("site2", min_delay=1.0)
    elapsed = time.time() - start
    assert elapsed < 0.1

def test_rate_limiter_reset():
    """Testa reset do rate limiter."""
    limiter = RateLimiter()
    
    limiter.wait_if_needed("test", min_delay=1.0)
    limiter.reset("test")
    
    # Após reset, não deve esperar
    start = time.time()
    limiter.wait_if_needed("test", min_delay=1.0)
    elapsed = time.time() - start
    assert elapsed < 0.1
