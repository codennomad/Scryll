#!/bin/bash

# Script de teste manual - execute este script para testar a configuração

echo "🔍 Testando configuração do Scryll com VPN..."
echo ""

# 1. Verificar VPN
echo "1️⃣ Verificando VPN..."
if ip link show tun0 &>/dev/null; then
    CURRENT_IP=$(curl -s https://ipinfo.io/ip)
    echo "   ✅ VPN conectada - IP: $CURRENT_IP"
else
    echo "   ❌ VPN não conectada"
    echo "   💡 Execute: sudo openvpn --config jp-free-20.protonvpn.udp.ovpn --auth-user-pass vpn_credentials.txt --daemon"
    exit 1
fi

echo ""

# 2. Test site access
echo "2️⃣ Testando acesso ao ManhuaUS..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://manhuaus.com/")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "   ⚠️  HTTP $HTTP_CODE - Cloudflare ainda ativo (normal)"
else
    echo "   ✅ HTTP $HTTP_CODE"
fi

echo ""

# 3. Verificar circuit breaker
echo "3️⃣ Status do Circuit Breaker..."
cd /home/kaspian/Scryll
./scryllenv/bin/python3 -c "
from core.circuit_breaker import circuit_breaker
state = circuit_breaker.get_state('manhuaus')
if state == 'OPEN':
    print('   ⚠️  Circuit breaker OPEN - resetando...')
    circuit_breaker.reset('manhuaus')
    print('   ✅ Resetado')
else:
    print('   ✅ Circuit breaker: ' + state)
"

echo ""

# 4. Verificar métricas
echo "4️⃣ Métricas atuais..."
./scryllenv/bin/python3 -c "
from core.metrics import metrics_collector
metrics_collector.print_summary()
"

echo ""
echo "=========================================="
echo "✅ Teste completo!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Teste manual: python3 main.py"
echo "   2. Copie serviço: sudo cp scryll.service /etc/systemd/system/"
echo "   3. Recarregue: sudo systemctl daemon-reload"
echo "   4. Habilite: sudo systemctl enable scryll.timer"
echo "   5. Inicie: sudo systemctl start scryll.timer"
echo "=========================================="
