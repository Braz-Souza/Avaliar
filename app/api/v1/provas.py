"""
Router para endpoints de gerenciamento de provas
"""

from fastapi import APIRouter, Depends

from app.models.prova import ProvaData, ProvaInfo
from app.services.prova_manager import ProvaManagerService

router = APIRouter(prefix="/provas", tags=["Provas Management"])


def get_prova_manager() -> ProvaManagerService:
    """
    Dependency para obter instância do serviço de provas
    
    Returns:
        ProvaManagerService
    """
    return ProvaManagerService()


@router.post("", response_model=ProvaInfo, status_code=201)
async def save_prova(
    prova: ProvaData,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> ProvaInfo:
    """
    Salva uma nova prova no servidor
    
    Args:
        prova: Dados da prova (nome e conteúdo LaTeX)
        manager: Serviço de gerenciamento (injetado)
        
    Returns:
        ProvaInfo com informações da prova salva
    """
    return await manager.save_prova(prova)


@router.get("", response_model=list[ProvaInfo])
async def list_provas(
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> list[ProvaInfo]:
    """
    Lista todas as provas salvas
    
    Args:
        manager: Serviço de gerenciamento (injetado)
        
    Returns:
        Lista de ProvaInfo ordenadas por data de modificação
    """
    return await manager.list_provas()


@router.get("/{prova_id}", response_model=ProvaData)
async def get_prova(
    prova_id: str,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> ProvaData:
    """
    Recupera o conteúdo de uma prova salva
    
    Args:
        prova_id: ID da prova
        manager: Serviço de gerenciamento (injetado)
        
    Returns:
        ProvaData com nome e conteúdo
    """
    return await manager.get_prova(prova_id)


@router.put("/{prova_id}", response_model=ProvaInfo)
async def update_prova(
    prova_id: str,
    prova: ProvaData,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> ProvaInfo:
    """
    Atualiza uma prova existente
    
    Args:
        prova_id: ID da prova
        prova: Novos dados da prova
        manager: Serviço de gerenciamento (injetado)
        
    Returns:
        ProvaInfo com informações atualizadas
    """
    return await manager.update_prova(prova_id, prova)


@router.delete("/{prova_id}")
async def delete_prova(
    prova_id: str,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> dict:
    """
    Exclui uma prova salva
    
    Args:
        prova_id: ID da prova
        manager: Serviço de gerenciamento (injetado)
        
    Returns:
        Dicionário com mensagem de sucesso
    """
    return await manager.delete_prova(prova_id)
