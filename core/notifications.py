import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
from loguru import logger

# Load .env with explicit path so it works regardless of CWD
_env_path = Path('/home/kaspian/Scryll/.env')
load_dotenv(_env_path, override=True)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def notify_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning('Telegram not configured: TOKEN={} CHAT_ID={}', bool(TELEGRAM_BOT_TOKEN), bool(TELEGRAM_CHAT_ID))
        return

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.ok:
            logger.info('Telegram notification sent: {}', resp.json().get('ok'))
        else:
            logger.error('Telegram API error {}: {}', resp.status_code, resp.text)
    except Exception as e:
        logger.error('Failed to send Telegram notification: {}', e)
