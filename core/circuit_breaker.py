"""Circuit Breaker para prevenir requisições repetidas a sites falhando."""

import time
from enum import Enum
from typing import Dict
from loguru import logger

class CircuitState(Enum):
    """Estados do circuit breaker."""
    CLOSED = "closed"      # Funcionando normalmente
    OPEN = "open"          # Bloqueado por muitas falhas
    HALF_OPEN = "half_open"  # Testando recuperação

class CircuitBreaker:
    """
    Circuit Breaker pattern para proteger de sites falhando.
    
    - CLOSED: Funcionamento normal
    - OPEN: Após N falhas consecutivas, bloqueia requisições
    - HALF_OPEN: Após timeout, permite testar se recuperou
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 300.0,  # 5 minutos
        half_open_max_attempts: int = 1
    ):
        """
        Args:
            failure_threshold: Número de falhas para abrir circuito
            recovery_timeout: Tempo em segundos antes de tentar novamente
            half_open_max_attempts: Tentativas no estado HALF_OPEN
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_attempts = half_open_max_attempts
        
        self._circuits: Dict[str, dict] = {}
    
    def _get_circuit(self, name: str) -> dict:
        """Obtém ou cria circuito para um site."""
        if name not in self._circuits:
            self._circuits[name] = {
                "state": CircuitState.CLOSED,
                "failures": 0,
                "last_failure_time": None,
                "half_open_attempts": 0
            }
        return self._circuits[name]
    
    def call(self, name: str, func, *args, **kwargs):
        """
        Executa função através do circuit breaker.
        
        Args:
            name: Nome do circuito (geralmente nome do site)
            func: Função a executar
            *args, **kwargs: Argumentos para a função
            
        Returns:
            Resultado da função
            
        Raises:
            Exception: Se circuito estiver OPEN
            Exception: Se função falhar
        """
        circuit = self._get_circuit(name)
        
        # Verifica estado do circuito
        if circuit["state"] == CircuitState.OPEN:
            # Verifica se pode tentar recuperação
            if self._should_attempt_reset(circuit):
                logger.info(f"🔄 Circuit breaker {name}: tentando recuperação (HALF_OPEN)")
                circuit["state"] = CircuitState.HALF_OPEN
                circuit["half_open_attempts"] = 0
            else:
                time_remaining = self._time_until_retry(circuit)
                raise Exception(
                    f"Circuit breaker OPEN para '{name}'. "
                    f"Tente novamente em {time_remaining:.0f}s"
                )
        
        # Tenta executar função
        try:
            result = func(*args, **kwargs)
            self._on_success(name)
            return result
            
        except Exception as e:
            self._on_failure(name)
            raise
    
    def _on_success(self, name: str):
        """Registra sucesso."""
        circuit = self._get_circuit(name)
        
        if circuit["state"] == CircuitState.HALF_OPEN:
            logger.success(f"✅ Circuit breaker {name}: recuperado (CLOSED)")
            circuit["state"] = CircuitState.CLOSED
        
        circuit["failures"] = 0
        circuit["half_open_attempts"] = 0
    
    def _on_failure(self, name: str):
        """Registra falha."""
        circuit = self._get_circuit(name)
        circuit["failures"] += 1
        circuit["last_failure_time"] = time.time()
        
        if circuit["state"] == CircuitState.HALF_OPEN:
            circuit["half_open_attempts"] += 1
            
            if circuit["half_open_attempts"] >= self.half_open_max_attempts:
                logger.warning(
                    f"⚠️ Circuit breaker {name}: falhou em HALF_OPEN, voltando para OPEN"
                )
                circuit["state"] = CircuitState.OPEN
        
        elif circuit["failures"] >= self.failure_threshold:
            logger.error(
                f"🔴 Circuit breaker {name}: ABERTO após {circuit['failures']} falhas. "
                f"Aguarde {self.recovery_timeout/60:.0f} minutos"
            )
            circuit["state"] = CircuitState.OPEN
    
    def _should_attempt_reset(self, circuit: dict) -> bool:
        """Verifica se deve tentar recuperação."""
        if circuit["last_failure_time"] is None:
            return False
        
        elapsed = time.time() - circuit["last_failure_time"]
        return elapsed >= self.recovery_timeout
    
    def _time_until_retry(self, circuit: dict) -> float:
        """Tempo até próxima tentativa."""
        if circuit["last_failure_time"] is None:
            return 0
        
        elapsed = time.time() - circuit["last_failure_time"]
        return max(0, self.recovery_timeout - elapsed)
    
    def get_state(self, name: str) -> CircuitState:
        """Obtém estado do circuito."""
        circuit = self._get_circuit(name)
        return circuit["state"]
    
    def is_available(self, name: str) -> bool:
        """Verifica se circuito está disponível."""
        state = self.get_state(name)
        return state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)
    
    def reset(self, name: str):
        """Reseta circuito manualmente."""
        if name in self._circuits:
            self._circuits[name] = {
                "state": CircuitState.CLOSED,
                "failures": 0,
                "last_failure_time": None,
                "half_open_attempts": 0
            }
            logger.info(f"🔄 Circuit breaker {name}: resetado manualmente")
    
    def get_summary(self) -> dict:
        """Retorna resumo de todos os circuitos."""
        return {
            name: {
                "state": circuit["state"].value,
                "failures": circuit["failures"],
                "available": self.is_available(name)
            }
            for name, circuit in self._circuits.items()
        }


# Instância global
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=300.0,  # 5 minutos
    half_open_max_attempts=1
)
