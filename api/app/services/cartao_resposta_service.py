"""
Serviço para geração de cartão resposta em PDF a partir de template HTML
"""

from pathlib import Path
from datetime import datetime
import logging
from typing import Optional

from weasyprint import HTML

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

    def generate_pdf(self, filename: Optional[str] = None) -> tuple[bool, str, Optional[Path]]:
        """
        Gera PDF do cartão resposta a partir do template HTML

        Args:
            filename: Nome do arquivo de saída (sem extensão). Se None, gera nome automático

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
