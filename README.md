# 📚 Scryll - Monitor Automático de Mangás/Manhuas

Sistema robusto e escalável para monitorar e baixar automaticamente novos capítulos de mangás/manhuas de diversos sites, com notificações em tempo real via Telegram.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Características

- 🔄 **Monitoramento Automático**: Verifica novos capítulos periodicamente
- 📥 **Download Inteligente**: Baixa apenas capítulos novos, evitando duplicatas
- 📢 **Notificações Telegram**: Alertas instantâneos de novos capítulos
- 🛡️ **Anti-Cloudflare**: Bypass automático de proteção Cloudflare
- 🔁 **Retry com Backoff**: Tentativas automáticas com delay exponencial
- 📊 **Métricas Detalhadas**: Estatísticas de sucesso/falha por site
- 🚦 **Rate Limiting**: Controle de requisições para evitar bloqueios
- 📝 **Logs Estruturados**: Logging rico com rotação automática
- ✅ **Validação Robusta**: Valida configurações no startup
- 🧪 **Testes**: Suite de testes unitários

## 🎯 Sites Suportados

- **ManhuaUS** - manhuas em português
- **MangaDex** - mangás em pt-br e inglês
- **ComicPark** - diversos mangás
- **RF Dragon Scans** - scanlations
- **VortexScans** - mangás populares

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Git

### Setup Rápido

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/scryll.git
cd scryll

# Crie ambiente virtual
python3 -m venv scryllenv
source scryllenv/bin/activate  # Linux/Mac
# ou
scryllenv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais
nano .env
```

### Configuração do Telegram

1. Crie um bot com [@BotFather](https://t.me/BotFather)
2. Copie o token recebido
3. Descubra seu chat_id com [@userinfobot](https://t.me/userinfobot)
4. Adicione ao arquivo `.env`:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## ⚙️ Configuração

### Adicionando Mangás

Edite `config.json` para adicionar mangás a monitorar:

```json
[
  {
    "name": "Solo Leveling",
    "site": "manhuaus",
    "url": "https://manhuaus.com/manga/solo-leveling/"
  },
  {
    "name": "One Piece",
    "site": "mangadex",
    "url": "https://mangadex.org/title/a1c7c817-4e59-43b7-9365-09675a149a6f"
  }
]
```

**Campos obrigatórios:**
- `name`: Nome do mangá (usado para organizar downloads)
- `site`: Site de origem (veja lista acima)
- `url`: URL completa da página do mangá

## 🚀 Uso

### Execução Manual

```bash
python3 main.py
```

### Automação com Systemd (Linux)

1. Edite os arquivos de serviço com seus caminhos:

```bash
# scryll.service
[Service]
WorkingDirectory=/seu/caminho/para/Scryll
ExecStart=/usr/bin/python3 /seu/caminho/para/Scryll/main.py
EnvironmentFile=/seu/caminho/para/Scryll/.env
```

2. Instale e ative:

```bash
sudo cp scryll.service /etc/systemd/system/
sudo cp scryll.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable scryll.timer
sudo systemctl start scryll.timer
```

3. Verifique status:

```bash
systemctl status scryll.timer
journalctl -u scryll.service -f  # Logs em tempo real
```

### Automação com Cron

```bash
# Edite o crontab
crontab -e

# Execute a cada 3 horas
0 */3 * * * cd /caminho/para/Scryll && ./scryllenv/bin/python3 main.py
```

## 📂 Estrutura do Projeto

```
Scryll/
├── core/
│   ├── config.py          # Validação de configurações
│   ├── downloader.py      # Lógica de download
│   ├── exceptions.py      # Exceções customizadas
│   ├── metrics.py         # Sistema de métricas
│   ├── models.py          # Modelos de dados
│   ├── notifications.py   # Notificações Telegram
│   ├── retry.py          # Retry e rate limiting
│   └── utils.py          # Utilitários
├── scrapers/
│   ├── manhuaus.py       # Scraper ManhuaUS
│   ├── mangadex.py       # Scraper MangaDex
│   ├── comicpark.py      # Scraper ComicPark
│   ├── rfdragonscan.py   # Scraper RF Dragon
│   └── vortexscans.py    # Scraper VortexScans
├── tests/                # Testes unitários
├── logs/                 # Logs da aplicação
├── downloads/            # Capítulos baixados
├── config.json           # Configuração de mangás
├── downloaded.json       # Controle de downloads
├── metrics.json          # Métricas persistidas
├── main.py              # Ponto de entrada
└── requirements.txt     # Dependências

```

## 📊 Métricas e Monitoramento

O Scryll coleta automaticamente métricas de cada scraper:

- Taxa de sucesso/falha
- Capítulos encontrados e baixados
- Erros de Cloudflare, rede e parsing
- Falhas consecutivas

Veja o resumo ao final de cada execução ou em `metrics.json`.

## 🧪 Testes

```bash
# Instale dependências de teste
pip install pytest pytest-cov

# Execute testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=core --cov=scrapers
```

## 🐛 Troubleshooting

### Erro 403 Cloudflare

O Scryll usa `cloudscraper` para bypass, mas sites muito protegidos podem bloquear. Soluções:

1. **Aguarde**: IPs bloqueados temporariamente normalizam em 1-2 horas
2. **Aumente delays**: Edite `.env` e aumente `RATE_LIMIT_DELAY`
3. **Use VPN**: Troque seu IP público

### Testes falhando

```bash
# Reinstale dependências
pip install -r requirements.txt --force-reinstall

# Limpe cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Notificações não chegam

```bash
# Teste o bot manualmente
curl -X POST "https://api.telegram.org/bot<SEU_TOKEN>/sendMessage" \
  -d "chat_id=<SEU_CHAT_ID>&text=Teste"
```

## 🔒 Segurança

- ✅ `.env` no `.gitignore` (nunca commite credenciais)
- ✅ Validação de entradas
- ✅ Tratamento seguro de exceções
- ✅ Logs não expõem dados sensíveis

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Adicionando Novos Scrapers

Crie um arquivo em `scrapers/` seguindo o padrão:

```python
from core.models import Chapter
from core.retry import retry_with_backoff, rate_limiter
from core.exceptions import NetworkException

@retry_with_backoff()
def fetch_chapters(manga_url: str) -> list[Chapter]:
    rate_limiter.wait_if_needed("meusite")
    # Sua lógica aqui
    return chapters
```

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- Comunidade Python
- Criadores do BeautifulSoup e requests
- Todos que contribuíram com scrapers

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/scryll/issues)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/scryll/discussions)

---

Feito com ❤️ para a comunidade de mangás/manhuas
