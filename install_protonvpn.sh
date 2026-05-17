#!/bin/bash
# Script de instalação do ProtonVPN

echo "🚀 Instalando ProtonVPN..."
echo ""

# Opção 1: Via pacman (requer sudo)
echo "📦 Opção 1: Instalação via pacman (recomendado)"
echo "Execute:"
echo "  sudo pacman -S python-protonvpn-cli openvpn"
echo ""

# Opção 2: Via pip no ambiente virtual
echo "📦 Opção 2: Instalação no ambiente virtual do Scryll"
echo "Execute:"
echo "  cd /home/kaspian/Scryll"
echo "  ./scryllenv/bin/pip install protonvpn-cli"
echo "  sudo pacman -S openvpn  # OpenVPN é necessário"
echo ""

# Opção 3: Download manual
echo "📦 Opção 3: Via GitHub (sem pacote)"
echo "  git clone https://github.com/ProtonVPN/linux-cli.git"
echo "  cd linux-cli"
echo "  sudo python3 setup.py install"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Após instalar, configure:"
echo "  1. protonvpn-cli login"
echo "  2. protonvpn-cli connect --fastest"
echo "  3. python3 main.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
