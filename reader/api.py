"""Scryll Reader API - with JWT authentication."""
import os
import re
import json
import sys
import threading
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── paths ────────────────────────────────────────────────────────────────────
SCRYLL_DIR   = Path("/home/kaspian/Scryll")
DOWNLOADS_DIR = SCRYLL_DIR / "downloads"
FRONTEND_DIR  = SCRYLL_DIR / "reader" / "dist"
CONFIG_PATH   = SCRYLL_DIR / "config.json"
ENV_PATH      = SCRYLL_DIR / "reader" / ".env"

sys.path.insert(0, str(SCRYLL_DIR))
load_dotenv(ENV_PATH)

JWT_SECRET    = os.getenv("JWT_SECRET", "change-me")
ALGORITHM     = "HS256"
TOKEN_DAYS    = 7
PASSWORD_HASH = os.getenv("PASSWORD_HASH", "")

bearer = HTTPBearer()

SITE_MAP = {
    "manhuaus.com":     "manhuaus",
    "mangadex.org":     "mangadex",
    "comicpark.net":    "comicpark",
    "vortexscans.com":  "vortexscans",
}

# ── rate limiter (in-memory, 5 attempts / 15 min per IP) ─────────────────────
class _RateLimiter:
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self._attempts: dict[str, list[datetime]] = defaultdict(list)
        self._lock = threading.Lock()
        self._max = max_attempts
        self._window = timedelta(minutes=window_minutes)

    def check(self, ip: str) -> bool:
        """Returns True if allowed, False if blocked."""
        with self._lock:
            now = datetime.now()
            self._attempts[ip] = [t for t in self._attempts[ip] if now - t < self._window]
            if len(self._attempts[ip]) >= self._max:
                return False
            self._attempts[ip].append(now)
            return True

rate_limiter = _RateLimiter()

# ── jwt helpers ───────────────────────────────────────────────────────────────
def _create_token() -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS)
    return jwt.encode({"sub": "admin", "exp": exp}, JWT_SECRET, algorithm=ALGORITHM)


def _verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get("sub") != "admin":
            raise HTTPException(403, "Token inválido")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(403, "Token inválido")


# ── app ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Scryll Reader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# ── auth endpoints (public) ───────────────────────────────────────────────────
class LoginRequest(BaseModel):
    password: str


@app.post("/api/auth/login")
def login(req: LoginRequest, request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host or "unknown").split(",")[0].strip()
    if not rate_limiter.check(ip):
        raise HTTPException(429, "Muitas tentativas. Tente novamente em 15 minutos.")
    if not PASSWORD_HASH or not bcrypt.checkpw(req.password.encode(), PASSWORD_HASH.encode()):
        raise HTTPException(401, "Senha incorreta")
    return {"token": _create_token()}


@app.get("/api/auth/me")
def me(_: dict = Depends(_verify_token)):
    return {"ok": True}


# ── library endpoints (all protected) ────────────────────────────────────────
def chapter_sort_key(name: str) -> float:
    m = re.search(r'chapter_(\d+(?:\.\d+)?)', name)
    return float(m.group(1)) if m else 0.0


def get_cover(series_path: Path, chapters: list) -> str | None:
    # Prefer official cover downloaded from source site
    for ext in ('webp', 'jpg', 'jpeg', 'png'):
        if (series_path / f'cover.{ext}').exists():
            return f"/api/image/{quote(series_path.name)}/cover.{ext}"
    # Fallback: first image of earliest chapter
    for chapter in chapters[:3]:
        cp = series_path / chapter
        if cp.is_dir():
            images = sorted(f for f in os.listdir(cp) if not f.startswith('.'))
            if images:
                return f"/api/image/{quote(series_path.name)}/{quote(chapter)}/{quote(images[0])}"
    return None


@app.get("/api/library")
def get_library(_: dict = Depends(_verify_token)):
    if not DOWNLOADS_DIR.exists():
        return []
    result = []
    for name in sorted(os.listdir(DOWNLOADS_DIR)):
        p = DOWNLOADS_DIR / name
        if not p.is_dir():
            continue
        chapters = sorted(
            [d for d in os.listdir(p) if d.startswith('chapter_')],
            key=chapter_sort_key,
        )
        if not chapters:
            continue
        result.append({
            "name": name,
            "chapter_count": len(chapters),
            "cover": get_cover(p, chapters),
            "latest_chapter": chapters[-1].replace('chapter_', ''),
            "first_chapter":  chapters[0].replace('chapter_', ''),
        })
    return result


@app.get("/api/series/{name:path}")
def get_series(name: str, _: dict = Depends(_verify_token)):
    p = DOWNLOADS_DIR / name
    if not p.is_dir():
        raise HTTPException(404, "Series not found")
    chapters = sorted(
        [d for d in os.listdir(p) if d.startswith('chapter_')],
        key=chapter_sort_key,
    )
    return {
        "name": name,
        "cover": get_cover(p, chapters),
        "chapter_count": len(chapters),
        "chapters": [
            {"id": c, "number": c.replace('chapter_', ''), "title": "Cap. " + c.replace('chapter_', '')}
            for c in chapters
        ],
    }


@app.get("/api/chapter/{name:path}/{chapter}")
def get_chapter(name: str, chapter: str, _: dict = Depends(_verify_token)):
    p = DOWNLOADS_DIR / name / chapter
    if not p.is_dir():
        raise HTTPException(404, "Chapter not found")
    images = sorted(f for f in os.listdir(p) if not f.startswith('.'))
    series_path = DOWNLOADS_DIR / name
    all_chapters = sorted(
        [d for d in os.listdir(series_path) if d.startswith('chapter_')],
        key=chapter_sort_key,
    )
    idx = all_chapters.index(chapter) if chapter in all_chapters else -1
    return {
        "series":         name,
        "chapter":        chapter,
        "number":         chapter.replace('chapter_', ''),
        "images":         [f"/api/image/{quote(name)}/{quote(chapter)}/{quote(img)}" for img in images],
        "prev":           all_chapters[idx - 1] if idx > 0 else None,
        "next":           all_chapters[idx + 1] if idx < len(all_chapters) - 1 else None,
        "chapter_index":  idx,
        "total_chapters": len(all_chapters),
    }


@app.get("/api/image/{path:path}")
def get_image(path: str):
    # No JWT required: img tags can't send Authorization headers.
    # The image paths are opaque without first querying protected endpoints.
    file_path = DOWNLOADS_DIR / path
    if not file_path.is_file():
        raise HTTPException(404, "Image not found")
    return FileResponse(str(file_path))


@app.get("/api/config")
def get_config(_: dict = Depends(_verify_token)):
    if not CONFIG_PATH.exists():
        return []
    return json.loads(CONFIG_PATH.read_text())


class AddMangaRequest(BaseModel):
    url: str


@app.post("/api/manga/add")
def add_manga(req: AddMangaRequest, _: dict = Depends(_verify_token)):
    url = req.url.strip().rstrip('/') + '/'
    site = next((s for d, s in SITE_MAP.items() if d in url), None)
    if not site:
        raise HTTPException(400, f"Site não suportado. Suportados: {', '.join(SITE_MAP.keys())}")

    config = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else []
    if any(i["url"].rstrip('/') + '/' == url for i in config):
        raise HTTPException(409, "Este manhwa já está na biblioteca")

    name = None
    cover_url = None
    try:
        from core import cf_bypass
        from bs4 import BeautifulSoup
        html = cf_bypass.fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        el = (soup.select_one(".post-title h1") or soup.select_one("h1"))
        if el:
            name = el.get_text(strip=True)
        for selector in ['.summary_image img', '.tab-summary .summary_image img', '.post-thumbnail img']:
            img = soup.select_one(selector)
            if img:
                src = img.get('data-src') or img.get('src') or ''
                if src.startswith('http'):
                    cover_url = src.strip()
                    break
    except Exception:
        pass

    if not name:
        slug = url.rstrip('/').split('/manga/')[-1].strip('/')
        name = ' '.join(w.capitalize() for w in slug.replace('-', ' ').split())

    config.append({"name": name, "site": site, "url": url})
    CONFIG_PATH.write_text(json.dumps(config, indent=4, ensure_ascii=False))

    # Download cover immediately (best-effort)
    if cover_url:
        try:
            from core import cf_bypass as _cfb
            series_dir = DOWNLOADS_DIR / name
            series_dir.mkdir(parents=True, exist_ok=True)
            ext = cover_url.split('.')[-1].split('?')[0].lower()
            if ext not in ('webp', 'jpg', 'jpeg', 'png'):
                ext = 'jpg'
            img_bytes = _cfb.fetch_image(cover_url, url)
            (series_dir / f'cover.{ext}').write_bytes(img_bytes)
        except Exception:
            pass

    return {"ok": True, "name": name, "site": site, "url": url}


@app.delete("/api/manga/remove")
def remove_manga(url: str, _: dict = Depends(_verify_token)):
    if not CONFIG_PATH.exists():
        raise HTTPException(404)
    config = json.loads(CONFIG_PATH.read_text())
    new = [i for i in config if i["url"].rstrip('/') + '/' != url.rstrip('/') + '/']
    if len(new) == len(config):
        raise HTTPException(404, "Não encontrado")
    CONFIG_PATH.write_text(json.dumps(new, indent=4, ensure_ascii=False))
    return {"ok": True}


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
