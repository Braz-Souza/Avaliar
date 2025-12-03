"""
Serviço para geração de cartão resposta em PDF a partir de template HTML
"""

from pathlib import Path
from datetime import datetime
import logging
from typing import Optional, Dict, Tuple
import base64
from io import BytesIO

from weasyprint import HTML
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

from app.core.config import settings

logger = logging.getLogger(__name__)


class CartaoRespostaService:
    """
    Serviço para geração de cartão resposta em PDF
    """

    def __init__(self):
        """Inicializa o serviço"""
        self.template_path = Path(__file__).parent.parent.parent / "static" / "templates" / "cartao_resposta.html"
        self.output_dir = settings.TEMP_PDF_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(
        self,
        filename: Optional[str] = None,
        student_name: Optional[str] = None,
        student_matricula: Optional[str] = None,
        exam_date: Optional[str] = None,
        turma_prova_id: Optional[str] = None
    ) -> tuple[bool, str, Optional[Path]]:
        """
        Gera PDF do cartão resposta a partir do template HTML

        Args:
            filename: Nome do arquivo de saída (sem extensão). Se None, gera nome automático
            student_name: Nome do aluno (opcional)
            student_matricula: Matrícula do aluno (opcional)
            exam_date: Data da prova (opcional). Se None, usa data atual
            turma_prova_id: id da relacao prova turma (Opcional)

        Returns:
            Tupla (sucesso, mensagem, caminho_pdf)
        """
        try:
            # Verifica se o template existe
            if not self.template_path.exists():
                error_msg = f"Template HTML não encontrado: {self.template_path}"
                logger.error(error_msg)
                return False, error_msg, None

            # Define nome do arquivo de saída
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cartao_resposta_{timestamp}"

            # Remove extensão se fornecida
            if filename.endswith('.pdf'):
                filename = filename[:-4]

            output_path = self.output_dir / f"{filename}.pdf"

            # Lê o HTML
            with open(self.template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Adicionar data
            if exam_date:
                html_content = html_content.replace('{{DATE}}', exam_date)
            else:
                # Usa data atual no formato brasileiro
                current_date = datetime.now().strftime("%d/%m/%Y")
                html_content = html_content.replace('{{DATE}}', current_date)

            # Adicionar informações do aluno se fornecidos
            if student_matricula:
                html_content = html_content.replace('{{STUDENT_MATRICULA}}', student_matricula)
                # Gerar QR Code com a matrícula
                qr_base64 = self._generate_qr_code(f"{student_matricula}/{turma_prova_id}")
                if qr_base64:
                    html_content = html_content.replace('{{QR_CODE}}', f'data:image/png;base64,{qr_base64}')
                else:
                    # Se falhou gerar QR, remove a seção
                    html_content = html_content.replace('<div class="qr-code-section" id="qr-section">', '<div class="qr-code-section" id="qr-section" style="display:none;">')
                    html_content = html_content.replace('{{QR_CODE}}', '')
            else:
                html_content = html_content.replace('{{STUDENT_MATRICULA}}', '')
                # Remove a seção do QR code se não há matrícula
                html_content = html_content.replace('<div class="qr-code-section" id="qr-section">', '<div class="qr-code-section" id="qr-section" style="display:none;">')
                html_content = html_content.replace('{{QR_CODE}}', '')
                
            if student_name:
                html_content = html_content.replace('{{STUDENT_NAME}}', student_name)
            else:
                html_content = html_content.replace('{{STUDENT_NAME}}', '')

            if student_matricula:
                html_content = html_content.replace('{{STUDENT_MATRICULA}}', student_matricula)
                # Gerar QR Code com a matrícula
                qr_base64 = self._generate_qr_code(f"{student_matricula}-{turma_prova_id}")
                if qr_base64:
                    html_content = html_content.replace('{{QR_CODE}}', f'data:image/png;base64,{qr_base64}')
                else:
                    # Se falhou gerar QR, remove a seção
                    html_content = html_content.replace('<div class="qr-code-section" id="qr-section">', '<div class="qr-code-section" id="qr-section" style="display:none;">')
                    html_content = html_content.replace('{{QR_CODE}}', '')
            else:
                html_content = html_content.replace('{{STUDENT_MATRICULA}}', '')
                # Remove a seção do QR code se não há matrícula
                html_content = html_content.replace('<div class="qr-code-section" id="qr-section">', '<div class="qr-code-section" id="qr-section" style="display:none;">')
                html_content = html_content.replace('{{QR_CODE}}', '')

            # Converte HTML para PDF usando WeasyPrint
            logger.info(f"Gerando PDF: {output_path}")
            HTML(string=html_content).write_pdf(output_path)

            if output_path.exists():
                logger.info(f"PDF gerado com sucesso: {output_path}")
                return True, "Cartão resposta gerado com sucesso", output_path
            else:
                error_msg = "PDF não foi criado"
                logger.error(error_msg)
                return False, error_msg, None

        except Exception as e:
            error_msg = f"Erro ao gerar PDF do cartão resposta: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None
        
    def _generate_qr_code(self, data: str) -> str:
        """
        Gera um QR Code e retorna como string base64 para embedding no HTML

        Args:
            data: Dados a serem codificados no QR Code (ex: matrícula do aluno)

        Returns:
            String base64 da imagem PNG do QR Code
        """
        try:
            # Criar QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Gerar imagem
            img = qr.make_image(fill_color="black", back_color="white")

            # Converter para base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()

            logger.debug(f"QR Code gerado com sucesso para: {data}")
            return img_base64

        except Exception as e:
            logger.error(f"Erro ao gerar QR Code: {str(e)}", exc_info=True)
            return ""

    def get_pdf_blob(self, pdf_path: Path) -> Optional[bytes]:
        """
        Lê o conteúdo do PDF como bytes

        Args:
            pdf_path: Caminho do arquivo PDF

        Returns:
            Conteúdo do PDF em bytes ou None se houver erro
        """
        try:
            if not pdf_path.exists():
                logger.error(f"PDF não encontrado: {pdf_path}")
                return None

            with open(pdf_path, 'rb') as f:
                return f.read()

        except Exception as e:
            logger.error(f"Erro ao ler PDF: {str(e)}", exc_info=True)
            return None

    def read_qr_code(self, image_bytes: bytes) -> Tuple[bool, str, Optional[Dict[str, str]]]:
        """
        Lê QR code de uma imagem e extrai os dados

        Args:
            image_bytes: Bytes da imagem contendo o QR code

        Returns:
            Tupla (sucesso, mensagem, dados)
            dados é um dict com 'matricula' e 'turma_prova_id'
        """
        try:
            # Abre a imagem a partir dos bytes
            img = Image.open(BytesIO(image_bytes))
            
            # Decodifica o QR code
            decoded_objects = decode(img)
            
            if not decoded_objects:
                return False, "Nenhum QR code encontrado na imagem", None
            
            # Pega o primeiro QR code encontrado
            qr_data = decoded_objects[0].data.decode('utf-8')
            
            # O formato esperado é "matricula/turma_prova_id"
            parts = qr_data.split('/')
            
            if len(parts) != 2:
                return False, f"Formato de QR code inválido. Esperado 'matricula/turma_prova_id', recebido: {qr_data}", None
            
            data = {
                "matricula": parts[0],
                "turma_prova_id": parts[1]
            }
            
            logger.info(f"QR code lido com sucesso: {data}")
            return True, "QR code lido com sucesso", data
            
        except Exception as e:
            error_msg = f"Erro ao ler QR code: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None

