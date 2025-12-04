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
import cv2
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class CartaoRespostaService:
    """
    Serviço para geração de cartão resposta em PDF
    """

    def __init__(self):
        """Inicializa o serviço"""
        self.template_path = Path(__file__).parent.parent.parent / "static" / "templates" / "cartao_resposta.html"
        self.omr_marker_path = Path(__file__).parent.parent.parent / "static" / "imgs" / "omr_marker.jpg"
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

            # Adicionar marcador OMR
            omr_marker_base64 = self._get_omr_marker_base64()
            if omr_marker_base64:
                html_content = html_content.replace('{{OMR_MARKER}}', f'data:image/jpeg;base64,{omr_marker_base64}')
            else:
                html_content = html_content.replace('{{OMR_MARKER}}', '')

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

    def _get_omr_marker_base64(self) -> str:
        """
        Lê a imagem do marcador OMR e retorna como string base64 para embedding no HTML

        Returns:
            String base64 da imagem JPEG do marcador OMR
        """
        try:
            if not self.omr_marker_path.exists():
                logger.warning(f"Imagem do marcador OMR não encontrada: {self.omr_marker_path}")
                return ""

            with open(self.omr_marker_path, 'rb') as f:
                img_bytes = f.read()
                img_base64 = base64.b64encode(img_bytes).decode()
                logger.debug("Marcador OMR convertido para base64 com sucesso")
                return img_base64

        except Exception as e:
            logger.error(f"Erro ao ler marcador OMR: {str(e)}", exc_info=True)
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

    def _detect_and_extract_qr_code(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Detecta e extrai a região do QR code de uma imagem usando OpenCV
        
        Args:
            image_bytes: Bytes da imagem
            
        Returns:
            Array numpy da região extraída do QR code ou None se não encontrado
        """
        try:
            # Converter bytes para array numpy
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Falha ao decodificar imagem")
                return None
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar blur gaussiano
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detectar bordas
            edged = cv2.Canny(blurred, 75, 200)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                logger.warning("Nenhum contorno encontrado na imagem")
                return None
            
            # Lista de candidatos a QR code
            qr_candidates = []
            
            for c in contours:
                # Aproximar o contorno
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                
                # QR codes têm 4 cantos (forma quadrada)
                if len(approx) == 4:
                    # Obter bounding box
                    x, y, w, h = cv2.boundingRect(approx)
                    area = cv2.contourArea(c)
                    
                    # Filtrar por tamanho (QR codes não são muito pequenos nem muito grandes)
                    if w < 50 or h < 50:  # muito pequeno
                        continue
                    if area > (image.shape[0] * image.shape[1] * 0.3):  # muito grande
                        continue
                    
                    # QR codes são aproximadamente quadrados
                    aspect_ratio = float(w) / h
                    if aspect_ratio < 0.85 or aspect_ratio > 1.15:
                        continue
                    
                    # Extrair região de interesse
                    roi = gray[y:y+h, x:x+w]
                    if roi.size == 0:
                        continue
                    
                    # Aplicar threshold para obter imagem binária
                    _, thresh = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY)
                    
                    # Contar proporção de pixels pretos
                    black_pixels = np.sum(thresh == 0)
                    white_pixels = np.sum(thresh == 255)
                    total_pixels = black_pixels + white_pixels
                    
                    if total_pixels == 0:
                        continue
                    
                    black_ratio = black_pixels / total_pixels
                    
                    # QR codes tipicamente têm 30-70% de pixels pretos
                    if 0.3 <= black_ratio <= 0.7:
                        qr_candidates.append((area, approx, black_ratio))
            
            if not qr_candidates:
                logger.warning("Nenhum candidato a QR code encontrado")
                return None
            
            # Ordenar candidatos pela proporção mais próxima de 50% de pixels pretos
            qr_candidates.sort(key=lambda x: abs(x[2] - 0.5))
            
            # Pegar o melhor candidato
            best_candidate = qr_candidates[0][1]
            
            # Aplicar transformação de perspectiva de 4 pontos
            # Ordenar os pontos: topo-esquerda, topo-direita, inferior-direita, inferior-esquerda
            pts = best_candidate.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            
            # Soma: topo-esquerda terá a menor soma, inferior-direita a maior
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            
            # Diferença: topo-direita terá a menor diferença, inferior-esquerda a maior
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            # Calcular largura e altura da nova imagem
            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(widthA), int(widthB))
            
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(heightA), int(heightB))
            
            # Pontos de destino
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]
            ], dtype="float32")
            
            # Calcular matriz de transformação e aplicar
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(gray, M, (maxWidth, maxHeight))
            
            logger.info(f"QR code detectado e extraído com sucesso. Tamanho: {maxWidth}x{maxHeight}")
            return warped
            
        except Exception as e:
            logger.error(f"Erro ao detectar QR code com OpenCV: {str(e)}", exc_info=True)
            return None
    
    def read_qr_code(self, image_bytes: bytes) -> Tuple[bool, str, Optional[Dict[str, str]]]:
        """
        Lê QR code de uma imagem e extrai os dados
        Primeiro tenta detectar e extrair o QR code com OpenCV, 
        depois decodifica com pyzbar

        Args:
            image_bytes: Bytes da imagem contendo o QR code

        Returns:
            Tupla (sucesso, mensagem, dados)
            dados é um dict com 'matricula' e 'turma_prova_id'
        """
        try:
            # Tentar detectar e extrair QR code com OpenCV
            qr_region = self._detect_and_extract_qr_code(image_bytes)
            
            # Se conseguiu extrair, converter para PIL Image
            if qr_region is not None:
                # Converter array numpy para PIL Image
                img = Image.fromarray(qr_region)
                logger.info("Tentando decodificar QR code da região extraída")
            else:
                # Se não conseguiu extrair, tentar com a imagem original
                logger.info("Não conseguiu extrair região do QR code, tentando com imagem original")
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

