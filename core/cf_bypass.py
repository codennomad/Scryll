"""Cloudflare bypass: curl-cffi (fast, no browser) + playwright (cookie refresh once per 20h)."""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

COOKIE_FILE = Path("/home/kaspian/Scryll/cf_cookies.json")
COOKIE_TTL_HOURS = 20


def _load_cookies() -> dict:
    if COOKIE_FILE.exists():
        try:
            return json.loads(COOKIE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_cookies(data: dict):
    try:
        COOKIE_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        logger.error("Falha ao salvar cookies: {}", e)


def _is_valid(domain: str, cookies_data: dict) -> bool:
    if domain not in cookies_data:
        return False
    expiry = cookies_data[domain].get("expiry")
    if not expiry:
        return False
    return datetime.fromisoformat(expiry) > datetime.now()


def _refresh_with_playwright(url: str, domain: str) -> dict:
    """Use playwright headless Chrome to solve Cloudflare and get cf_clearance cookie."""
    logger.info("Abrindo Chrome para resolver Cloudflare em {}...", domain)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                      "--single-process", "--memory-pressure-off"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            logger.info("Carregando {} e aguardando Cloudflare resolver (40s)...", url)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception:
                pass
            for _ in range(8):
                time.sleep(5)
                cookies = context.cookies()
                cf_cookie = next((c for c in cookies if c["name"] == "cf_clearance"), None)
                if cf_cookie:
                    logger.success("cf_clearance obtido!")
                    break
            cookies = context.cookies()
            browser.close()
            result = {c["name"]: c["value"] for c in cookies}
            logger.info("Playwright terminou com {} cookies", len(result))
            return result
    except ImportError:
        logger.error("playwright nao instalado.")
        return {}
    except Exception as e:
        logger.error("Erro no playwright: {}", e)
        return {}


def _get_cookies(url: str) -> dict:
    """Return valid cookies for domain, refreshing via playwright if needed."""
    domain = url.split("/")[2]
    cookies_data = _load_cookies()

    if _is_valid(domain, cookies_data):
        logger.debug("Usando cookies em cache para {}", domain)
        return cookies_data[domain]["cookies"]

    logger.info("Cookies expirados/ausentes para {}, renovando...", domain)
    new_cookies = _refresh_with_playwright(url, domain)

    # Always save to cache (even empty dict) so playwright is not launched every call
    cookies_data[domain] = {
        "cookies": new_cookies,
        "expiry": (datetime.now() + timedelta(hours=COOKIE_TTL_HOURS)).isoformat()
    }
    _save_cookies(cookies_data)
    logger.info("Cache de cookies salvo para {} (expira em {}h)", domain, COOKIE_TTL_HOURS)
    return new_cookies


def fetch(url: str) -> str:
    """Fetch URL bypassing Cloudflare. Uses curl-cffi with cached cf_clearance cookie."""
    try:
        from curl_cffi import requests as cf_requests
    except ImportError:
        logger.error("curl-cffi nao instalado. Execute: pip install curl-cffi")
        raise

    domain = url.split("/")[2]
    cookies = _get_cookies(url)

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": f"https://{domain}/",
    }

    response = cf_requests.get(url, impersonate="chrome120", cookies=cookies,
                                headers=headers, timeout=30)

    # If still blocked, invalidate cache and retry once
    if "Just a moment" in response.text or ("cloudflare" in response.text.lower() and response.status_code in (403, 503)):
        logger.warning("Ainda bloqueado, invalidando cache e retentando...")
        cookies_data = _load_cookies()
        if domain in cookies_data:
            del cookies_data[domain]
            _save_cookies(cookies_data)
        cookies = _get_cookies(url)
        response = cf_requests.get(url, impersonate="chrome120", cookies=cookies,
                                    headers=headers, timeout=30)

    response.raise_for_status()
    return response.text


def fetch_image(url: str, referer: str) -> bytes:
    """Fetch image bytes bypassing Cloudflare hotlink protection."""
    try:
        from curl_cffi import requests as cf_requests
    except ImportError:
        import requests
        r = requests.get(url, headers={"Referer": referer}, timeout=30)
        r.raise_for_status()
        return r.content

    domain = url.split("/")[2]
    cookies = _get_cookies(referer)
    headers = {
        "Referer": referer,
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }
    response = cf_requests.get(url, impersonate="chrome120", cookies=cookies,
                                headers=headers, timeout=30)
    response.raise_for_status()
    return response.content
