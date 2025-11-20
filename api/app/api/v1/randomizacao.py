"""
Router para endpoints de randomização de provas

TODAS AS ROTAS REQUEREM AUTENTICAÇÃO (via middleware global)
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.db.models.randomizacao import TurmaProvaRead, AlunoRandomizacaoRead
from app.services.randomizacao_manager import RandomizacaoManagerService
from app.services.turma_manager import TurmaManagerService
from app.services.prova_manager import ProvaManagerService
from app.services.latex_compiler import LaTeXCompilerService
from app.services.gabarito_service import GabaritoService
from app.core.database import get_db
from app.core.dependencies import CurrentUser

router = APIRouter(prefix="/randomizacao", tags=["Randomização Management"])


def get_randomizacao_manager(db: Session = Depends(get_db)) -> RandomizacaoManagerService:
    """
    Dependency para obter instância do serviço de randomização com sessão do banco

    Args:
        db: Sessão do banco de dados

    Returns:
        RandomizacaoManagerService com sessão do banco
    """
    return RandomizacaoManagerService(db)


def get_turma_manager(db: Session = Depends(get_db)) -> TurmaManagerService:
    """
    Dependency para obter instância do serviço de turmas com sessão do banco

    Args:
        db: Sessão do banco de dados

    Returns:
        TurmaManagerService com sessão do banco
    """
    return TurmaManagerService(db)


def get_prova_manager(db: Session = Depends(get_db)) -> ProvaManagerService:
    """
    Dependency para obter instância do serviço de provas com sessão do banco

    Args:
        db: Sessão do banco de dados

    Returns:
        ProvaManagerService com sessão do banco
    """
    return ProvaManagerService(db)


def get_latex_compiler() -> LaTeXCompilerService:
    """
    Dependency para obter instância do serviço de compilação LaTeX

    Returns:
        LaTeXCompilerService
    """
    return LaTeXCompilerService()


@router.post("/link/{turma_id}/{prova_id}", response_model=TurmaProvaRead, status_code=201)
async def link_prova_to_turma(
    turma_id: UUID,
    prova_id: UUID,
    user_id: CurrentUser,
    manager: RandomizacaoManagerService = Depends(get_randomizacao_manager)
) -> TurmaProvaRead:
    """
    Liga uma prova a uma turma e cria randomização para cada aluno - REQUER AUTENTICAÇÃO

    Args:
        turma_id: ID da turma
        prova_id: ID da prova
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de randomização (injetado)

    Returns:
        TurmaProvaRead com informações da ligação criada

    Raises:
        HTTPException: Se turma ou prova não existirem, ou se já estiverem vinculadas
    """
    try:
        return await manager.link_prova_to_turma(turma_id, prova_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao vincular prova à turma: {str(e)}")


@router.get("/turmas-provas", response_model=List[TurmaProvaRead])
async def list_turmas_provas(
    user_id: CurrentUser,
    turma_id: Optional[UUID] = Query(None, description="ID da turma para filtrar"),
    prova_id: Optional[UUID] = Query(None, description="ID da prova para filtrar"),
    manager: RandomizacaoManagerService = Depends(get_randomizacao_manager)
) -> List[TurmaProvaRead]:
    """
    Lista vínculos entre turmas e provas com filtros opcionais - REQUER AUTENTICAÇÃO

    Args:
        user_id: ID do usuário autenticado (injetado pelo middleware)
        turma_id: ID da turma para filtrar (opcional)
        prova_id: ID da prova para filtrar (opcional)
        manager: Serviço de randomização (injetado)

    Returns:
        Lista de TurmaProvaRead
    """
    try:
        return await manager.get_turmas_provas(turma_id=turma_id, prova_id=prova_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar vínculos: {str(e)}")


@router.get("/alunos/{turma_prova_id}", response_model=List[AlunoRandomizacaoRead])
async def get_alunos_randomizacoes(
    turma_prova_id: UUID,
    user_id: CurrentUser,
    manager: RandomizacaoManagerService = Depends(get_randomizacao_manager)
) -> List[AlunoRandomizacaoRead]:
    """
    Obtém randomizações de todos os alunos de uma turma-prova - REQUER AUTENTICAÇÃO

    Args:
        turma_prova_id: ID da ligação turma-prova
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de randomização (injetado)

    Returns:
        Lista de AlunoRandomizacaoRead com dados dos alunos

    Raises:
        HTTPException: Se turma_prova_id não existir
    """
    try:
        return await manager.get_aluno_randomizacoes(turma_prova_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter randomizações: {str(e)}")


@router.get("/aluno/{aluno_id}/prova/{prova_id}", response_model=AlunoRandomizacaoRead)
async def get_aluno_randomizacao(
    aluno_id: UUID,
    prova_id: UUID,
    user_id: CurrentUser,
    manager: RandomizacaoManagerService = Depends(get_randomizacao_manager)
) -> AlunoRandomizacaoRead:
    """
    Obtém randomização específica de um aluno para uma prova - REQUER AUTENTICAÇÃO

    Args:
        aluno_id: ID do aluno
        prova_id: ID da prova
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de randomização (injetado)

    Returns:
        AlunoRandomizacaoRead com dados da randomização

    Raises:
        HTTPException: Se randomização não for encontrada
    """
    try:
        randomizacao = await manager.get_aluno_randomizacao(aluno_id, prova_id)
        if not randomizacao:
            raise HTTPException(status_code=404, detail="Randomização não encontrada")
        return randomizacao
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter randomização: {str(e)}")


@router.get("/aluno/{aluno_id}/prova/{prova_id}/content")
async def get_aluno_prova_content(
    aluno_id: UUID,
    prova_id: UUID,
    user_id: CurrentUser,
    manager: RandomizacaoManagerService = Depends(get_randomizacao_manager),
    latex_compiler: LaTeXCompilerService = Depends(get_latex_compiler)
):
    """
    Retorna o PDF da prova personalizada para um aluno - REQUER AUTENTICAÇÃO

    Args:
        aluno_id: ID do aluno
        prova_id: ID da prova
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de randomização (injetado)
        latex_compiler: Serviço de compilação LaTeX (injetado)

    Returns:
        Response com PDF da prova personalizada

    Raises:
        HTTPException: Se randomização não for encontrada ou erro na compilação
    """
    try:
        # Obter conteúdo personalizado
        content = await manager.get_aluno_prova_content(aluno_id, prova_id)

        # Compilar para PDF
        success, pdf_bytes, error = await latex_compiler.compile_to_bytes(
            latex_content=content,
            filename=f"prova_{aluno_id}_{prova_id}"
        )

        if not success:
            raise HTTPException(status_code=500, detail=f"Erro ao compilar PDF: {error}")

        # Retornar PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=prova_aluno_{aluno_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF da prova: {str(e)}")


@router.delete("/unlink/{turma_id}/{prova_id}")
async def unlink_prova_from_turma(
    turma_id: UUID,
    prova_id: UUID,
    user_id: CurrentUser,
    manager: RandomizacaoManagerService = Depends(get_randomizacao_manager)
) -> dict:
    """
    Remove vinculo entre prova e turma (exclui todas as randomizações) - REQUER AUTENTICAÇÃO

    Args:
        turma_id: ID da turma
        prova_id: ID da prova
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de randomização (injetado)

    Returns:
        Dicionário com mensagem de sucesso

    Raises:
        HTTPException: Se vínculo não for encontrado
    """
    try:
        success = await manager.unlink_prova_from_turma(turma_id, prova_id)
        if not success:
            raise HTTPException(status_code=404, detail="Vínculo não encontrado")
        return {"message": "Vínculo removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover vínculo: {str(e)}")


@router.get("/turmas/disponiveis/{prova_id}")
async def get_turmas_disponiveis_para_prova(
    prova_id: UUID,
    user_id: CurrentUser,
    turma_manager: TurmaManagerService = Depends(get_turma_manager),
    randomizacao_manager: RandomizacaoManagerService = Depends(get_randomizacao_manager)
) -> dict:
    """
    Lista turmas disponíveis para vincular a uma prova - REQUER AUTENTICAÇÃO

    Args:
        prova_id: ID da prova
        user_id: ID do usuário autenticado (injetado pelo middleware)
        turma_manager: Serviço de turmas (injetado)
        randomizacao_manager: Serviço de randomização (injetado)

    Returns:
        Dicionário com turmas disponíveis e já vinculadas
    """
    try:
        # Obter todas as turmas
        todas_turmas = await turma_manager.list_turmas()

        # Obter turmas já vinculadas a esta prova
        vinculacoes = await randomizacao_manager.get_turmas_provas(prova_id=prova_id)
        turmas_vinculadas_ids = {vp.turma_id for vp in vinculacoes}

        # Separar turmas disponíveis e vinculadas
        turmas_disponiveis = [t for t in todas_turmas if t.id not in turmas_vinculadas_ids]
        turmas_vinculadas = [t for t in todas_turmas if t.id in turmas_vinculadas_ids]

        return {
            "disponiveis": turmas_disponiveis,
            "vinculadas": turmas_vinculadas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar turmas disponíveis: {str(e)}")


@router.get("/provas/disponiveis/{turma_id}")
async def get_provas_disponiveis_para_turma(
    turma_id: UUID,
    user_id: CurrentUser,
    prova_manager: ProvaManagerService = Depends(get_prova_manager),
    randomizacao_manager: RandomizacaoManagerService = Depends(get_randomizacao_manager)
) -> dict:
    """
    Lista provas disponíveis para vincular a uma turma - REQUER AUTENTICAÇÃO

    Args:
        turma_id: ID da turma
        user_id: ID do usuário autenticado (injetado pelo middleware)
        prova_manager: Serviço de provas (injetado)
        randomizacao_manager: Serviço de randomização (injetado)

    Returns:
        Dicionário com provas disponíveis e já vinculadas
    """
    try:
        # Obter todas as provas
        todas_provas = await prova_manager.list_provas()

        # Obter provas já vinculadas a esta turma
        vinculacoes = await randomizacao_manager.get_turmas_provas(turma_id=turma_id)
        provas_vinculadas_ids = {vp.prova_id for vp in vinculacoes}

        # Separar provas disponíveis e vinculadas
        provas_disponiveis = [p for p in todas_provas if p.id not in provas_vinculadas_ids]
        provas_vinculadas = [p for p in todas_provas if p.id in provas_vinculadas_ids]

        return {
            "disponiveis": provas_disponiveis,
            "vinculadas": provas_vinculadas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar provas disponíveis: {str(e)}")


@router.get("/download-zip/{turma_prova_id}")
async def download_all_provas_zip(
    turma_prova_id: UUID,
    user_id: CurrentUser,
    manager: RandomizacaoManagerService = Depends(get_randomizacao_manager),
    latex_compiler: LaTeXCompilerService = Depends(get_latex_compiler)
):
    """
    Baixa arquivo ZIP contendo todas as provas personalizadas dos alunos - REQUER AUTENTICAÇÃO

    Args:
        turma_prova_id: ID da ligação turma-prova
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de randomização (injetado)
        latex_compiler: Serviço de compilação LaTeX (injetado)

    Returns:
        Response com arquivo ZIP contendo todos os PDFs das provas

    Raises:
        HTTPException: Se turma_prova_id não existir ou erro na geração dos PDFs
    """
    try:
        # Criar ZIP com todos os PDFs
        zip_bytes, zip_filename = await manager.create_zip_with_all_pdfs(
            turma_prova_id=turma_prova_id,
            latex_compiler=latex_compiler
        )

        # Retornar ZIP
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ZIP das provas: {str(e)}")


@router.get("/gabarito/{aluno_id}/{prova_id}")
async def download_gabarito_aluno(
    aluno_id: UUID,
    prova_id: UUID,
    user_id: CurrentUser,
    manager: RandomizacaoManagerService = Depends(get_randomizacao_manager)
):
    """
    Baixa o gabarito personalizado em PDF para um aluno específico - REQUER AUTENTICAÇÃO

    Args:
        aluno_id: ID do aluno
        prova_id: ID da prova
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de randomização (injetado)

    Returns:
        Response com arquivo PDF do gabarito personalizado

    Raises:
        HTTPException: Se aluno/prova não existirem ou erro na geração do PDF
    """
    try:
        # Obter respostas corretas usando o serviço de randomização
        correct_answers = await manager.get_correct_answers_for_aluno(aluno_id, prova_id)

        # Usar GabaritoService para gerar o PDF
        gabarito_service = GabaritoService()
        success, message, pdf_path = gabarito_service.generate_pdf(
            correct_answers=correct_answers,
            filename=f"gabarito_aluno_{aluno_id}_prova_{prova_id}"
        )

        if not success or not pdf_path:
            raise HTTPException(status_code=500, detail=f"Erro ao gerar gabarito: {message}")

        # Ler o PDF e retornar
        pdf_bytes = gabarito_service.get_pdf_blob(pdf_path)
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Erro ao ler PDF do gabarito")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=gabarito_aluno_{aluno_id}.pdf"
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar gabarito: {str(e)}")
