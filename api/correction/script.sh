#!/bin/bash

# Script para processar imagem de prova com OMRChecker
# Recebe imagem da pasta images/ e processa com OMRChecker

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGES_DIR="$SCRIPT_DIR/images"
OMRCHECKER_DIR="$SCRIPT_DIR/OMRChecker"
FILES_DIR="$SCRIPT_DIR"

# Verificar se há imagens para processar
if [ ! -d "$IMAGES_DIR" ] || [ -z "$(ls -A "$IMAGES_DIR" 2>/dev/null)" ]; then
    echo "Nenhuma imagem encontrada em $IMAGES_DIR"
    exit 1
fi

# Pegar a imagem mais recente
LATEST_IMAGE=$(ls -t "$IMAGES_DIR"/* 2>/dev/null | head -n1)

if [ -z "$LATEST_IMAGE" ]; then
    echo "Nenhuma imagem encontrada"
    exit 1
fi

echo "Processando imagem: $LATEST_IMAGE"

# Limpar diretórios do OMRChecker
rm -rf "$OMRCHECKER_DIR/inputs"/*
rm -rf "$OMRCHECKER_DIR/outputs"/*

# Copiar template e omr_marker.jpg
cp "$FILES_DIR/template.json" "$OMRCHECKER_DIR/inputs/template.json"
cp "$FILES_DIR/omr_marker.jpg" "$OMRCHECKER_DIR/inputs/omr_marker.jpg"

# Criar estrutura de diretórios e copiar imagem
mkdir -p "$OMRCHECKER_DIR/inputs/avaliar"
cp "$LATEST_IMAGE" "$OMRCHECKER_DIR/inputs/avaliar/image.jpg"

# Executar OMRChecker (ele processa o diretório inputs/)
cd "$OMRCHECKER_DIR"

# Ativar ambiente virtual e executar
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python3 main.py
    RESULT=$?
    deactivate
else
    # Se não houver venv, tentar executar diretamente
    python3 main.py
    RESULT=$?
fi

cd "$SCRIPT_DIR"

# Verificar se o processamento foi bem-sucedido
if [ $RESULT -eq 0 ]; then
    # Copiar resultados
    if [ -d "$OMRCHECKER_DIR/outputs/avaliar/Results" ]; then
        cp "$OMRCHECKER_DIR/outputs/avaliar/Results"/*.csv "$SCRIPT_DIR/" 2>/dev/null || true
        echo "Processamento concluído com sucesso!"

        # Mostrar conteúdo do CSV se existir
        CSV_FILE=$(ls "$SCRIPT_DIR"/*.csv 2>/dev/null | head -n1)
        if [ -f "$CSV_FILE" ]; then
            echo "Resultados:"
            cat "$CSV_FILE"
        fi
    else
        echo "Aviso: Diretório de resultados não encontrado"
    fi
else
    echo "Erro ao executar OMRChecker (código: $RESULT)"
    exit $RESULT
fi

exit 0

