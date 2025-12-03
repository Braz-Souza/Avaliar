"""
Endpoint para processamento de imagens de correção
"""

import os
import subprocess
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query, Form
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
import shutil

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.models import (
    Correcao, CorrecaoCreate, CorrecaoRead, CorrecaoReadWithDetails,
    CorrecaoResposta, CorrecaoRespostaCreate,
    User, Aluno, Turma, Prova
)
from app.db.models.randomizacao import TurmaProva
from app.services.randomizacao_manager import RandomizacaoManagerService

router = APIRouter(
    prefix="/image-correction",
    tags=["Image Correction"],
)


@router.post("/upload", response_model=CorrecaoReadWithDetails)
async def upload_and_process_image(
    file: UploadFile = File(...),
    # Aceitar via Query Parameters
    aluno_id_query: Optional[str] = Query(None, alias="aluno_id", description="ID do aluno (query param)"),
    turma_id_query: Optional[str] = Query(None, alias="turma_id", description="ID da turma (query param)"),
    prova_id_query: Optional[str] = Query(None, alias="prova_id", description="ID da prova (query param)"),
    # Aceitar via Form Data
    aluno_id_form: Optional[str] = Form(None, alias="aluno_id", description="ID do aluno (form data)"),
    turma_id_form: Optional[str] = Form(None, alias="turma_id", description="ID da turma (form data)"),
    prova_id_form: Optional[str] = Form(None, alias="prova_id", description="ID da prova (form data)"),
    session: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
) -> CorrecaoReadWithDetails:
    """
    Recebe uma imagem de cartão resposta, processa usando OMR, e salva a correção no banco de dados.

    Os IDs podem ser enviados via query parameters OU via form data.

    Args:
        file: Arquivo de imagem do cartão resposta
        aluno_id: ID do aluno (query param ou form data)
        turma_id: ID da turma (query param ou form data)
        prova_id: ID da prova (query param ou form data)
        session: Sessão do banco de dados
        current_user_id: ID do usuário autenticado

    Returns:
        Correção completa com todas as respostas salvas
    """
    # Pegar os IDs de query params ou form data (o que estiver preenchido)
    aluno_id = aluno_id_query or aluno_id_form
    turma_id = turma_id_query or turma_id_form
    prova_id = prova_id_query or prova_id_form

    # Log para debug
    print(f"DEBUG - aluno_id recebido: {aluno_id} (query: {aluno_id_query}, form: {aluno_id_form})")
    print(f"DEBUG - turma_id recebido: {turma_id} (query: {turma_id_query}, form: {turma_id_form})")
    print(f"DEBUG - prova_id recebido: {prova_id} (query: {prova_id_query}, form: {prova_id_form})")
    print(f"DEBUG - current_user_id: {current_user_id}")

    # Validar que os IDs foram fornecidos
    if not aluno_id or not turma_id or not prova_id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "IDs obrigatórios não fornecidos",
                "aluno_id": aluno_id,
                "turma_id": turma_id,
                "prova_id": prova_id,
                "message": "Use query parameters: ?aluno_id=xxx&turma_id=yyy&prova_id=zzz"
            }
        )

    # Converter strings para UUID
    try:
        aluno_uuid = UUID(aluno_id)
        turma_uuid = UUID(turma_id)
        prova_uuid = UUID(prova_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"IDs devem ser UUIDs válidos: {str(e)}"
        )

    # Validar tipo de arquivo
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="O arquivo deve ser uma imagem"
        )

    # Validar se aluno, turma e prova existem
    aluno = session.get(Aluno, aluno_uuid)
    if not aluno:
        raise HTTPException(status_code=404, detail=f"Aluno com ID {aluno_id} não encontrado")

    turma = session.get(Turma, turma_uuid)
    if not turma:
        raise HTTPException(status_code=404, detail=f"Turma com ID {turma_id} não encontrada")

    prova = session.get(Prova, prova_uuid)
    if not prova or prova.deleted:
        raise HTTPException(status_code=404, detail=f"Prova com ID {prova_id} não encontrada")

    # Buscar o usuário corretor pelo username
    corretor = session.exec(select(User).where(User.username == current_user_id)).first()

    if not corretor:
        raise HTTPException(
            status_code=404,
            detail=f"Usuário corretor '{current_user_id}' não encontrado"
        )    # Definir caminhos
    api_dir = Path(__file__).parent.parent.parent.parent
    images_dir = api_dir / "correction" / "images"
    script_path = api_dir / "correction" / "script.sh"

    # Criar diretório se não existir
    images_dir.mkdir(parents=True, exist_ok=True)

    # Gerar nome do arquivo
    filename = file.filename or "uploaded_image.jpg"
    file_path = images_dir / filename

    try:
        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Executar script
        if not script_path.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Script não encontrado: {script_path}"
            )

        # Executar o script na pasta correction
        correction_dir = api_dir / "correction"
        result = subprocess.run(
            ["bash", "script.sh"],
            cwd=str(correction_dir),
            capture_output=True,
            text=True,
            timeout=300  # Timeout de 5 minutos
        )

        # Tentar ler o CSV gerado
        omr_results = {}
        csv_files = list(correction_dir.glob("*.csv"))

        if csv_files:
            try:
                csv_file = csv_files[0]  # Pegar o primeiro CSV encontrado
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    csv_data = list(reader)

                    # Processar os dados do CSV para o formato desejado
                    if csv_data:
                        # Pegar a primeira linha (assumindo que há apenas um cartão por imagem)
                        row = csv_data[0]

                        # Extrair as respostas (colunas que começam com 'q' seguido de número)
                        for key, value in row.items():
                            if key.startswith('q') and key[1:].isdigit():
                                question_num = int(key[1:])  # Remove o 'q' e converte para int
                                omr_results[question_num] = value if value else "?"

                # Limpar o arquivo CSV após leitura
                os.remove(csv_file)
            except Exception as csv_error:
                print(f"Erro ao ler CSV: {csv_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao processar arquivo CSV: {str(csv_error)}"
                )

        if not omr_results:
            raise HTTPException(
                status_code=500,
                detail="Nenhuma resposta foi detectada na imagem"
            )

        # Criar a correção no banco de dados
        total_questoes = len(omr_results)

        # Buscar TurmaProva pelo turma_id e prova_id
        turma_prova = session.exec(
            select(TurmaProva).where(
                TurmaProva.turma_id == turma_uuid,
                TurmaProva.prova_id == prova_uuid
            )
        ).first()

        if not turma_prova:
            raise HTTPException(
                status_code=404,
                detail=f"Não existe vínculo entre a turma {turma_id} e a prova {prova_id}"
            )

        # Buscar gabarito e calcular nota
        randomizacao_manager = RandomizacaoManagerService(session)
        gabarito = await randomizacao_manager.get_correct_answers_for_aluno(aluno_uuid, turma_prova.id)
        acertos = sum(1 for q, r in omr_results.items() if r and gabarito.get(q) and r.upper() == gabarito[q])
        nota = (acertos / total_questoes * 10) if total_questoes > 0 else 0

        correcao = Correcao(
            aluno_id=aluno_uuid,
            turma_id=turma_uuid,
            prova_id=prova_uuid,
            corrigido_por=corretor.id,
            data_correcao=datetime.utcnow(),
            total_questoes=total_questoes,
            acertos=acertos,
            nota=nota
        )

        session.add(correcao)
        session.commit()
        session.refresh(correcao)

        # Salvar cada resposta com validação
        for questao_numero, resposta_marcada in omr_results.items():
            resposta_correta = gabarito.get(questao_numero)
            esta_correta = (resposta_marcada.upper() == resposta_correta) if resposta_correta and resposta_marcada else None

            resposta = CorrecaoResposta(
                correcao_id=correcao.id,
                questao_numero=questao_numero,
                resposta_marcada=resposta_marcada,
                resposta_correta=resposta_correta,
                esta_correta=esta_correta
            )
            session.add(resposta)

        session.commit()
        session.refresh(correcao)

        # Retornar a correção completa com todas as relações
        return CorrecaoReadWithDetails(
            id=correcao.id,
            aluno_id=correcao.aluno_id,
            turma_id=correcao.turma_id,
            prova_id=correcao.prova_id,
            corrigido_por=correcao.corrigido_por,
            data_correcao=correcao.data_correcao,
            nota=correcao.nota,
            total_questoes=correcao.total_questoes,
            acertos=correcao.acertos,
            respostas=correcao.respostas,
            aluno=aluno,
            turma=turma,
            prova=prova,
            corretor=corretor
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Timeout ao executar o script de processamento"
        )
    except Exception as e:
        # Em caso de erro, tentar remover o arquivo
        if file_path.exists():
            try:
                os.remove(file_path)
            except:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar imagem: {str(e)}"
        )


@router.get("/correcoes", response_model=List[CorrecaoRead])
async def listar_correcoes(
    aluno_id: Optional[UUID] = None,
    turma_id: Optional[UUID] = None,
    prova_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
) -> List[CorrecaoRead]:
    """
    Lista todas as correções com filtros opcionais.

    Args:
        aluno_id: Filtrar por aluno (opcional)
        turma_id: Filtrar por turma (opcional)
        prova_id: Filtrar por prova (opcional)
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros a retornar
        session: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Lista de correções
    """
    statement = select(Correcao)

    if aluno_id:
        statement = statement.where(Correcao.aluno_id == aluno_id)
    if turma_id:
        statement = statement.where(Correcao.turma_id == turma_id)
    if prova_id:
        statement = statement.where(Correcao.prova_id == prova_id)

    statement = statement.offset(skip).limit(limit)

    correcoes = session.exec(statement).all()
    return correcoes


@router.get("/correcoes/{correcao_id}", response_model=CorrecaoReadWithDetails)
async def buscar_correcao(
    correcao_id: UUID,
    session: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
) -> CorrecaoReadWithDetails:
    """
    Busca uma correção específica por ID com todos os detalhes.

    Args:
        correcao_id: ID da correção
        session: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Correção com todos os detalhes e relacionamentos
    """
    correcao = session.get(Correcao, correcao_id)

    if not correcao:
        raise HTTPException(
            status_code=404,
            detail=f"Correção com ID {correcao_id} não encontrada"
        )

    # Carregar relacionamentos
    aluno = session.get(Aluno, correcao.aluno_id)
    turma = session.get(Turma, correcao.turma_id)
    prova = session.get(Prova, correcao.prova_id)
    corretor = session.get(User, correcao.corrigido_por)

    # Verificar se prova foi deletada
    if prova and prova.deleted:
        prova = None

    return CorrecaoReadWithDetails(
        id=correcao.id,
        aluno_id=correcao.aluno_id,
        turma_id=correcao.turma_id,
        prova_id=correcao.prova_id,
        corrigido_por=correcao.corrigido_por,
        data_correcao=correcao.data_correcao,
        nota=correcao.nota,
        total_questoes=correcao.total_questoes,
        acertos=correcao.acertos,
        respostas=correcao.respostas,
        aluno=aluno,
        turma=turma,
        prova=prova,
        corretor=corretor
    )


@router.delete("/correcoes/{correcao_id}")
async def deletar_correcao(
    correcao_id: UUID,
    session: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Deleta uma correção e todas as suas respostas.

    Args:
        correcao_id: ID da correção
        session: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Mensagem de sucesso
    """
    correcao = session.get(Correcao, correcao_id)

    if not correcao:
        raise HTTPException(
            status_code=404,
            detail=f"Correção com ID {correcao_id} não encontrada"
        )

    session.delete(correcao)
    session.commit()

    return {"message": f"Correção {correcao_id} deletada com sucesso"}
