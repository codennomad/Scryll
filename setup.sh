#!/bin/bash
# Script de setup automático para Scryll

set -e  # Para em caso de erro

echo "🚀 Iniciando setup do Scryll..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica Python
echo ""
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Instale Python 3.8+ primeiro.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION encontrado${NC}"

# Cria ambiente virtual
echo ""
echo "📦 Criando ambiente virtual..."
if [ -d "scryllenv" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual já existe${NC}"
else
    python3 -m venv scryllenv
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
fi

# Ativa ambiente virtual
echo ""
echo "🔌 Ativando ambiente virtual..."
source scryllenv/bin/activate

# Instala dependências
echo ""
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependências instaladas${NC}"

# Cria .env se não existir
echo ""
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Edite o arquivo .env com suas credenciais do Telegram${NC}"
    echo -e "${YELLOW}   nano .env${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
fi

# Cria config.json se não existir
echo ""
if [ ! -f "config.json" ]; then
    echo "📝 Criando config.json de exemplo..."
    cat > config.json << 'EOF'
[
  {
    "name": "Exemplo Manga",
    "site": "manhuaus",
    "url": "https://manhuaus.com/manga/seu-manga-aqui/"
  }
]
EOF
    echo -e "${YELLOW}⚠️  Edite config.json e adicione seus mangás${NC}"
    echo -e "${YELLOW}   nano config.json${NC}"
else
    echo -e "${GREEN}✅ config.json já existe${NC}"
fi

# Cria diretórios necessários
echo ""
echo "📁 Criando diretórios..."
mkdir -p logs downloads
echo -e "${GREEN}✅ Diretórios criados${NC}"

# Testa configuração
echo ""
echo "🧪 Testando configuração..."
if python3 -c "from core.config import validate_env_vars; validate_env_vars()" 2>/dev/null; then
    echo -e "${GREEN}✅ Validação básica OK${NC}"
else
    echo -e "${YELLOW}⚠️  Configure o .env antes de executar${NC}"
fi

# Resumo
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Setup concluído com sucesso!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos passos:"
echo "1. Edite .env com suas credenciais:"
echo "   nano .env"
echo ""
echo "2. Configure os mangás em config.json:"
echo "   nano config.json"
echo ""
echo "3. Execute o Scryll:"
echo "   python3 main.py"
echo ""
echo "4. (Opcional) Execute os testes:"
echo "   pytest tests/ -v"
echo ""
echo "5. (Opcional) Configure para executar automaticamente:"
echo "   - Veja README.md seção 'Automação'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
