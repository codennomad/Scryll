#!/bin/bash

# Script para executar Scryll com VPN automaticamente
# Usado pelo systemd timer

SCRIPT_DIR="/home/kaspian/Scryll"
cd "$SCRIPT_DIR"

echo "🔍 Verificando conexão VPN..."

# Verifica se VPN está conectada
if ! ip link show tun0 &>/dev/null; then
    echo "🔄 VPN não está conectada, conectando..."
    sudo /usr/bin/openvpn --config "$SCRIPT_DIR/jp-free-20.protonvpn.udp.ovpn" \
        --auth-user-pass "$SCRIPT_DIR/vpn_credentials.txt" \
        --daemon \
        --log /tmp/openvpn.log
    
    # Aguarda VPN conectar (máximo 15 segundos)
    for i in {1..15}; do
        if ip link show tun0 &>/dev/null; then
            echo "✅ VPN conectada!"
            sleep 2  # Aguarda estabilizar
            break
        fi
        echo "⏳ Aguardando VPN... ($i/15)"
        sleep 1
    done
    
    if ! ip link show tun0 &>/dev/null; then
        echo "❌ Falha ao conectar VPN"
        exit 1
    fi
else
    echo "✅ VPN já está conectada"
fi

# Verifica IP
CURRENT_IP=$(curl -s https://ipinfo.io/ip)
echo "🌍 IP atual: $CURRENT_IP"

# Reseta circuit breaker se necessário
echo "🔄 Resetando circuit breaker..."
"$SCRIPT_DIR/scryllenv/bin/python3" -c "from core.circuit_breaker import circuit_breaker; circuit_breaker.reset('manhuaus')" 2>/dev/null || true

# Executa Scryll
echo "🚀 Executando Scryll..."
"$SCRIPT_DIR/scryllenv/bin/python3" "$SCRIPT_DIR/main.py"

EXIT_CODE=$?
echo "✅ Scryll finalizado com código: $EXIT_CODE"
exit $EXIT_CODE
