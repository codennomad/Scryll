module.exports = {
  apps: [{
    name: 'scryll-reader',
    script: '/home/kaspian/Scryll/scryllenv/bin/uvicorn',
    args: 'api:app --host 127.0.0.1 --port 3003',
    cwd: '/home/kaspian/Scryll/reader',
    interpreter: 'none',
    env: { PYTHONPATH: '/home/kaspian/Scryll' }
  }]
}
