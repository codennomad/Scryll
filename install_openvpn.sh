#!/bin/bash
# Comando para instalar OpenVPN (requer senha sudo)

echo "🔐 OpenVPN é necessário para o ProtonVPN funcionar"
echo ""
echo "Execute este comando:"
echo ""
echo "  sudo pacman -S openvpn"
echo ""
echo "Após instalar, configure o ProtonVPN:"
echo "  ./scryllenv/bin/protonvpn-cli login"
echo "  ./scryllenv/bin/protonvpn-cli connect --fastest"
