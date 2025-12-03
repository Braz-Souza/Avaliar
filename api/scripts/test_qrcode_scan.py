"""
Script para testar o endpoint de scan de QR code
"""

import requests
from pathlib import Path

# URL do endpoint
API_URL = "http://localhost:8000/api/cartao-resposta/scan-qrcode"

def test_scan_qrcode(image_path: str):
    """
    Testa o endpoint de scan de QR code
    
    Args:
        image_path: Caminho para a imagem contendo o QR code
    """
    # Verifica se o arquivo existe
    if not Path(image_path).exists():
        print(f"❌ Arquivo não encontrado: {image_path}")
        return
    
    print(f"📤 Enviando imagem: {image_path}")
    
    try:
        # Abre o arquivo e faz o upload
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(API_URL, files=files)
        
        print(f"\n📊 Status: {response.status_code}")
        print(f"📄 Resposta: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                qr_data = data.get('data', {})
                print("\n✅ QR Code lido com sucesso!")
                print(f"   Matrícula: {qr_data.get('matricula')}")
                print(f"   Turma/Prova ID: {qr_data.get('turma_prova_id')}")
            else:
                print(f"\n❌ Erro: {data.get('message')}")
        else:
            print(f"\n❌ Erro HTTP: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python test_qrcode_scan.py <caminho_da_imagem>")
        print("\nExemplo:")
        print("  python test_qrcode_scan.py cartao_resposta.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_scan_qrcode(image_path)
