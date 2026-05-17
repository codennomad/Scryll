# 🔐 Status da Configuração - Scryll com VPN

## ✅ O que está funcionando:

### 1. **VPN ProtonVPN Conectada**
- ✅ IP Japonês ativo: `212.102.51.33`
- ✅ Conexão automática via `run_with_vpn.sh`
- ✅ Sudo sem senha configurado para OpenVPN
- ✅ Reconexão automática se desconectar

### 2. **Automação Completa**
- ✅ Timer systemd configurado (**a cada 3 horas**)
- ✅ Próxima execução programada automaticamente
- ✅ Circuit breaker reseta a cada execução
- ✅ Métricas salvas em `metrics.json`
- ✅ Logs em `logs/scryll.log` e `journalctl`

### 3. **Infraestrutura Robusta**
- ✅ Sistema de retry com backoff exponencial
- ✅ Circuit breaker após 5 falhas consecutivas
- ✅ Rate limiting (5s entre requisições)
- ✅ Tratamento de exceções robusto
- ✅ Testes automatizados (14 testes)

## ⚠️ Desafio Atual: Cloudflare "Under Attack" Mode

### O Problema:
O site **ManhuaUS.com** está usando Cloudflare em modo "Under Attack", que:
- Exige execução de JavaScript para resolver challenge
- Detecta automação mesmo com VPN
- Bloqueia ferramentas como `curl`, `requests`, `cloudscraper`
- Permite apenas navegadores reais (Chrome, Firefox, etc)

### O que já tentamos:
1. ✅ Headers completos de navegador
2. ✅ cloudscraper (simula Chrome)
3. ✅ VPN (IP japonês não bloqueado)
4. ✅ Selenium + undetected-chromedriver (crash por memória RAM insuficiente)
5. ✅ curl com user-agent
6. ✅ Delays maiores entre requisições

### Por que ainda não funciona:
O Cloudflare JavaScript challenge requer:
- **Execução de JavaScript** (subprocess/curl não suporta)
- **Renderização DOM** (requests/curl não suportam)
- **Navegador real** (Selenium crashou por falta de RAM: 3.71 GB total, processo precisa ~1.5-2GB)

## 💡 Soluções Possíveis:

### Opção 1: Aguardar o Cloudflare relaxar (RECOMENDADO)
- **Pro:** Gratuito, já configurado
- **Contra:** Impre visível (pode funcionar às vezes, às vezes não)
- **Como:** Simplesmente deixe rodando a cada 3 horas, eventualmente o Cloudflare vai permitir

### Opção 2: Upgrade de RAM para Selenium
- **Pro:** Selenium funciona em máquinas com mais RAM
- **Contra:** Requer hardware melhor (mínimo 8GB RAM)
- **Como:** Upgrade físico ou migrar para servidor com mais RAM

### Opção 3: Serviço de Scraping Profissional
- **Pro:** 99% de taxa de sucesso, gerenciado
- **Contra:** Pago (~$50-150/mês)
- **Opções:**
  - [ScraperAPI](https://www.scraperapi.com/) - $49/mês (1M requests)
  - [Bright Data](https://brightdata.com/) - $500/mês
  - [Oxylabs](https://oxylabs.io/) - $300/mês

### Opção 4: Usar site alternativo
- **Pro:** Pode ser mais fácil de scrapear
- **Contra:** Precisa encontrar fonte alternativa com mesmo conteúdo
- **Exemplos:** MangaDex, Manganato, etc (já configurados no Scryll)

## 🚀 Como Usar o Sistema Atual:

### Ver Status:
```bash
# Status do timer
systemctl status scryll.timer

# Quando vai executar próxima vez
systemctl list-timers scryll.timer

# Ver logs em tempo real
sudo journalctl -u scryll.service -f

# Ver métricas
cat /home/kaspian/Scryll/metrics.json
```

### Executar Manualmente:
```bash
cd /home/kaspian/Scryll
./run_with_vpn.sh
```

### Testar VPN:
```bash
# Ver IP atual
curl https://ipinfo.io/ip

# Deve mostrar: 212.102.51.33 (Japão)
```

### Desabilitar/Habilitar Automação:
```bash
# Desabilitar
sudo systemctl stop scryll.timer
sudo systemctl disable scryll.timer

# Habilitar
sudo systemctl enable scryll.timer
sudo systemctl start scryll.timer
```

## 📊 Métricas Atuais:

```
Sites: 1 (manhuaus)
Taxa de sucesso: 0.0%
Falhas consecutivas: 30
Última tentativa: 2026-02-04 00:18
Motivo: Cloudflare JavaScript challenge
```

## 🔮 Próximos Passos Sugeridos:

1. **Curto Prazo:** Deixe rodando automático, Cloudflare pode relaxar
2. **Médio Prazo:** Considere outros scrapers (MangaDex, etc)
3. **Longo Prazo:** Se crítico, invista em serviço profissional ou hardware

## 📁 Arquivos Importantes:

- `/home/kaspian/Scryll/run_with_vpn.sh` - Script principal
- `/home/kaspian/Scryll/scryll.service` - Configuração systemd
- `/home/kaspian/Scryll/scryll.timer` - Timer de 3 horas
- `/home/kaspian/Scryll/vpn_credentials.txt` - Credenciais VPN (protegido)
- `/home/kaspian/Scryll/logs/scryll.log` - Logs da aplicação
- `/home/kaspian/Scryll/metrics.json` - Métricas de sucesso/falha

## 🛠️ Troubleshooting:

**VPN não conecta:**
```bash
sudo systemctl status openvpn
sudo openvpn --config jp-free-20.protonvpn.udp.ovpn --auth-user-pass vpn_credentials.txt --daemon
```

**Timer não executa:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart scryll.timer
```

**Verificar circuit breaker:**
```bash
./scryllenv/bin/python3 -c "from core.circuit_breaker import circuit_breaker; print(circuit_breaker.get_state('manhuaus'))"
```

---

**Sistema desenvolvido com:**
- Python 3.13
- ProtonVPN (Japão)
- systemd timers
- Circuit Breaker pattern
- Retry with exponential backoff
- Comprehensive logging

**Última atualização:** 2026-02-04 00:20
