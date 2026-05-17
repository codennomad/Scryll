#!/usr/bin/env python3
"""
Script para analisar a estrutura HTML do ManhuaUS e encontrar os seletores corretos.
"""

import sys
sys.path.insert(0, '/home/kaspian/Scryll')

from bs4 import BeautifulSoup
import subprocess
import re

print("🔍 Analisando estrutura do ManhuaUS com VPN...")
print()

# Baixa a página com curl (usando VPN)
url = "https://manhuaus.com/manga/god-level-assassin-im-the-shadow/"
cmd = f'''curl -sL "{url}" \
-H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
-H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
-H "Accept-Language: en-US,en;q=0.5" \
-H "Referer: https://manhuaus.com/" \
--compressed'''

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
html = result.stdout

print(f"📄 HTML baixado: {len(html)} caracteres")

# Verifica se é Cloudflare
if "Just a moment" in html or "cf_chl_opt" in html:
    print("❌ Cloudflare JavaScript Challenge detectado")
    print("   O site requer JavaScript para carregar.")
    print()
    print("💡 Solução: Precisamos usar Selenium com espera mais longa")
    print("   O problema é que o Selenium está crashando por falta de memória.")
    print()
    print("📝 Alternativas:")
    print("   1. Usar Selenium headless com --no-sandbox e --disable-dev-shm-usage")
    print("   2. Testar em outro site menos protegido")
    print("   3. Usar um proxy residencial + cloudscraper")
    sys.exit(1)

# Parse HTML
soup = BeautifulSoup(html, 'html.parser')

print()
print("🔎 Procurando possíveis seletores de capítulos...")
print()

# Procura por diferentes padrões
patterns = [
    ("wp-manga-chapter", "a"),
    ("chapter-item", "a"),
    ("chapter-link", None),
    ("chapter", "a"),
    ("manga-chapter", "a"),
    ("listing-chapters_wrap", "a"),
    ("version-chap", "a"),
]

found_any = False

for class_name, tag in patterns:
    elements = soup.find_all(class_=class_name)
    if elements:
        print(f"✅ Encontrado: .{class_name} ({len(elements)} elementos)")
        found_any = True
        
        # Mostra exemplo
        for i, elem in enumerate(elements[:3]):
            if tag:
                link = elem.find(tag)
                if link:
                    print(f"   Exemplo {i+1}: {link.get('href', 'N/A')} - {link.get_text(strip=True)[:50]}")
            else:
                print(f"   Exemplo {i+1}: {elem.get('href', 'N/A')} - {elem.get_text(strip=True)[:50]}")
        print()

if not found_any:
    print("❌ Nenhum seletor comum encontrado")
    print()
    print("📋 Classes encontradas no HTML:")
    all_classes = set()
    for tag in soup.find_all(class_=True):
        if isinstance(tag.get('class'), list):
            all_classes.update(tag.get('class'))
    
    # Filtra apenas classes relacionadas a chapter/manga
    chapter_classes = [c for c in all_classes if 'chapter' in c.lower() or 'manga' in c.lower()]
    if chapter_classes:
        for cls in sorted(chapter_classes)[:10]:
            print(f"   • {cls}")
    else:
        print("   Nenhuma classe relacionada a 'chapter' encontrada")
        print(f"   Total de classes: {len(all_classes)}")

print()
print("🔗 Procurando links que contenham 'chapter'...")
chapter_links = soup.find_all('a', href=re.compile(r'chapter', re.I))
if chapter_links:
    print(f"✅ Encontrados {len(chapter_links)} links com 'chapter' na URL")
    for i, link in enumerate(chapter_links[:5]):
        print(f"   {i+1}. {link.get('href')} - {link.get_text(strip=True)[:50]}")
else:
    print("❌ Nenhum link com 'chapter' encontrado")
