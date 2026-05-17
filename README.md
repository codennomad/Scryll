# Scryll

> Manga and manhwa reader — self-hosted, private, zero tracking.

Scryll is a self-hosted manga/manhwa reading platform. It scrapes licensed sources on demand using a resilient Python pipeline (Cloudflare bypass, rotating proxies, Selenium fallback) and serves the content through a clean React reader with JWT-authenticated access.

---

## Architecture

```
Scryll/
├── core/          Python scraping engine
├── scrapers/      Site-specific scraper modules
├── reader/
│   ├── api.py     FastAPI backend (JWT auth, chapter serving)
│   └── frontend/  React reader UI (Vite)
├── main.py        CLI entry point
└── tests/
```

---

## Stack

### Scraping Engine

| Technology | Role |
|---|---|
| Python 3.12 | Runtime |
| requests / httpx | HTTP client |
| Selenium | Cloudflare JS challenge bypass |
| SlowAPI | Rate limiting |
| asyncio | Concurrent downloads |

### Reader

| Technology | Role |
|---|---|
| FastAPI | REST API (chapter data, auth) |
| PyJWT + bcrypt | Authentication |
| React + Vite | Frontend reader UI |
| PM2 | Process management |

---

## Features

- **Cloudflare bypass** — circuit-breaker backed CF challenge solver with Selenium fallback
- **Proxy rotation** — automatic proxy pool with health checks and circuit breakers
- **Retry logic** — exponential backoff with jitter on all HTTP requests
- **Metrics** — per-scrape tracking (success rate, latency, bandwidth)
- **Reader API** — JWT-protected chapter serving with auth (`/api/auth/me`, `/api/chapters`)
- **React reader** — clean UI for reading chapters page by page
- **PM2 deployment** — ecosystem config for production process management

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Chrome/Chromium (for Selenium fallback)

### Backend

```bash
# Create and activate virtual environment
python -m venv scryllenv
source scryllenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env and configure
cp .env.example .env
```

Edit `.env`:

```env
API_KEY=your-scraping-api-key
PROXY_LIST=proxy1:port,proxy2:port
```

```bash
# Run scraper CLI
python main.py
```

### Reader API + Frontend

```bash
cd reader

# Install Python deps
pip install -r requirements.txt

# Configure reader auth
cp .env.example .env   # add JWT_SECRET and PASSWORD_HASH

# Start API
uvicorn api:app --port 3003

# Build and serve frontend
cd frontend
npm install
npm run build
```

### Production (PM2)

```bash
cd reader
pm2 start ecosystem.config.cjs
pm2 save
```

---

## Core Modules

| Module | Description |
|---|---|
| `core/downloader.py` | Main download orchestrator |
| `core/cf_bypass.py` | Cloudflare challenge handler |
| `core/proxy_manager.py` | Rotating proxy pool with health checks |
| `core/circuit_breaker.py` | Circuit breaker for failing scrapers |
| `core/retry.py` | Exponential backoff retry decorator |
| `core/metrics.py` | Scrape metrics collection |
| `core/selenium_scraper.py` | Selenium-based fallback scraper |
| `scrapers/manhuaus.py` | manhuaus.com scraper module |

---

## Security

- Reader API protected by JWT — no public access to chapters
- Password stored as bcrypt hash — never in plaintext
- Credentials and VPN configs excluded from version control via `.gitignore`

---

## License

MIT — self-host responsibly.
