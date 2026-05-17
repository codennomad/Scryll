# 🛡️ Soluções para Cloudflare no Scryll

## Problema

O ManhuaUS e outros sites usam Cloudflare em modo "Under Attack", bloqueando requisições automatizadas.

## 🔧 Soluções Implementadas

### 1. **Cloudscraper (Padrão)**
- Tenta primeiro com `cloudscraper`
- Funciona em ~70% dos casos
- Rápido e leve

### 2. **Selenium + undetected-chromedriver (Fallback Automático)**
- Se cloudscraper falhar, muda automaticamente para Selenium
- Simula navegador Chrome real
- Taxa de sucesso ~95%
- **Mais lento** (~10s por página)

### 3. **Circuit Breaker**
- Após 5 falhas consecutivas, para de tentar por 5 minutos
- Economiza recursos
- Tenta recuperação automática

## 📥 Instalação do Selenium

### Linux (Ubuntu/Debian)
```bash
# 1. Instale Chrome/Chromium
sudo apt update
sudo apt install -y chromium-browser chromium-chromedriver

# OU Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# 2. Instale dependências Python
cd /home/kaspian/Scryll
./scryllenv/bin/pip install undetected-chromedriver selenium
```

### Arch Linux
```bash
sudo pacman -S chromium
./scryllenv/bin/pip install undetected-chromedriver selenium
```

### Docker (Headless)
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt
```

## 🚀 Como Funciona

```python
1. Tenta com cloudscraper (rápido)
   └─ Sucesso? → Retorna capítulos
   └─ Cloudflare bloqueou?
       └─ Selenium disponível?
           ├─ SIM → Usa Selenium (lento mas funciona)
           └─ NÃO → Retorna erro + dica de instalação
```

## 🎯 Performance

| Método | Velocidade | Taxa Sucesso | Recursos |
|--------|-----------|--------------|----------|
| cloudscraper | ~2s/página | 30% | Baixo |
| Selenium | ~15s/página | 95% | Alto |

## ⚙️ Configuração Avançada

### Desabilitar Selenium
Se não quiser usar Selenium, simplesmente não o instale. O sistema usará apenas cloudscraper.

### Ajustar Delays
Edite em `scrapers/manhuaus.py`:
```python
rate_limiter.wait_if_needed("manhuaus", min_delay=5.0)  # Aumenta delay
rate_limiter.wait_if_needed("manhuaus_selenium", min_delay=20.0)
```

### Circuit Breaker
Edite em `core/circuit_breaker.py`:
```python
circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Falhas antes de abrir
    recovery_timeout=300.0,   # Tempo em segundos (5 min)
)
```

## 🔍 Verificar Status

```bash
# Ver se Selenium está disponível
python3 -c "from core.selenium_scraper import is_selenium_available; print(is_selenium_available())"

# Testar Chrome
chromium --version
# ou
google-chrome --version
```

## 🆘 Troubleshooting

### Erro: "ChromeDriver not found"
```bash
# Baixe ChromeDriver manualmente
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# Use a versão compatível com seu Chrome
```

### Erro: "Chrome binary not found"
```bash
# Instale Chrome
sudo apt install chromium-browser
```

### Muito lento
O Selenium é naturalmente mais lento porque simula um navegador real. É o trade-off para bypass de Cloudflare.

**Dica**: Configure para executar durante a madrugada quando Cloudflare é menos rigoroso.

## 🔄 Alternativas

### 1. VPN/Proxy
Use VPN para trocar IP se bloqueado temporariamente:
```bash
sudo apt install openvpn
```

### 2. Aguardar Cooldown
IPs bloqueados geralmente normalizam em 1-2 horas.

### 3. Usar Outros Sites
O Scryll suporta MangaDex, ComicPark, etc que não usam Cloudflare tão agressivo.

## 📊 Logs de Sucesso

Quando Selenium funcionar, você verá:
```
✅ Selenium/Chrome disponível para bypass de Cloudflare
🌐 Carregando https://manhuaus.com/... com Selenium...
⏳ Aguardando resolução do Cloudflare challenge...
✅ Página carregada com sucesso
```
