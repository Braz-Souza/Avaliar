"""
Modelos Pydantic para gerenciamento de provas
"""

from pydantic import BaseModel


class ProvaData(BaseModel):
    """
    Modelo para dados completos de uma prova
    
    Attributes:
        name: Nome da prova
        content: Conteúdo LaTeX da prova
    """
    name: str
    content: str


class ProvaInfo(BaseModel):
    """
    Modelo para informações resumidas de uma prova
    
    Attributes:
        id: Identificador único da prova
        name: Nome da prova
        created_at: Data/hora de criação (ISO 8601)
        modified_at: Data/hora da última modificação (ISO 8601)
    """
    id: str
    name: str
    created_at: str
    modified_at: str
