#!/bin/bash

# Script de instalação rápida do OMRChecker
# Execute uma vez antes de usar o processamento de imagens

set -e  # Para na primeira erro

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OMRCHECKER_DIR="$SCRIPT_DIR/OMRChecker"

echo "🚀 Instalando OMRChecker..."

# Clonar repositório se não existir
if [ ! -d "$OMRCHECKER_DIR" ]; then
    echo "📦 Clonando repositório OMRChecker..."
    cd "$SCRIPT_DIR"
    git clone https://github.com/Udayraj123/OMRChecker.git
else
    echo "✓ OMRChecker já existe"
fi

cd "$OMRCHECKER_DIR"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "🐍 Criando ambiente virtual..."
    python3 -m venv venv
else
    echo "✓ Ambiente virtual já existe"
fi

# Ativar e instalar dependências
echo "📚 Instalando dependências..."
source venv/bin/activate
pip install --upgrade pip
pip install opencv-contrib-python
pip install -r requirements.txt

deactivate

echo ""
echo "✅ Instalação concluída com sucesso!"
echo "🎯 O sistema está pronto para processar imagens"
echo ""
