from datetime import datetime, timedelta
from functools import wraps
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.audit_service import AuditService
from app.core.auth import get_current_user
from app.core.logging_config import logger
from app.database import agora, get_db
from app.schemas.audit import ActivityHistoryListOut, LoginHistoryListOut, UserHistoryListOut
from app.schemas.user import CampoOrdenacaoAuditoria, EventoLogin, OrdemAuditoria

# Toda a auditoria exige token: o histórico, com os detalhes das operações, não pode ser público.
router = APIRouter(prefix="/auditoria", tags=["Auditoria"], dependencies=[Depends(get_current_user)])


def servico_auditoria(db: Session = Depends(get_db)) -> AuditService:
    return AuditService(db)


Auditoria = Annotated[AuditService, Depends(servico_auditoria)]


def _erro_500(mensagem: str):
    """Qualquer falha da consulta vira 500 com a mensagem dada (o detalhe vai só para o log)."""
    def decorador(funcao):
        @wraps(funcao)
        def envolvida(*args, **kwargs):
            try:
                return funcao(*args, **kwargs)
            except Exception as e:
                logger.error(f"{mensagem}: {e}")
                raise HTTPException(status_code=500, detail=mensagem) from e
        return envolvida
    return decorador


@router.get("/login-history", response_model=LoginHistoryListOut, summary="Histórico de logins/logouts com filtros")
@_erro_500("Erro ao consultar histórico de logins")
def get_login_history(
    auditoria: Auditoria,
    username: Optional[str] = Query(None, description="Filtrar por usuário (busca parcial)"),
    event_type: Optional[EventoLogin] = Query(None, description="Filtrar por tipo de evento"),
    sucesso: Optional[bool] = Query(None, description="Filtrar por sucesso (true/false)"),
    data_inicio: Optional[datetime] = Query(None, description="Data/hora de início (ISO 8601)"),
    data_fim: Optional[datetime] = Query(None, description="Data/hora de fim (ISO 8601)"),
    ordenar_por: CampoOrdenacaoAuditoria = Query(CampoOrdenacaoAuditoria.TIMESTAMP, description="Campo para ordenação"),
    ordem: OrdemAuditoria = Query(OrdemAuditoria.DESC, description="Direção da ordenação"),
    limite: int = Query(100, ge=1, le=1000, description="Máximo de registros"),
):
    """Retorna o histórico de logins/logouts com filtros e ordenação."""
    items = auditoria.listar_logins(
        username=username,
        event_type=event_type.value if event_type else None,
        sucesso=sucesso,
        data_inicio=data_inicio,
        data_fim=data_fim,
        ordenar_por=ordenar_por.value,
        ordem=ordem.value,
        limite=limite,
    )
    return {"total": len(items), "items": items}


@router.get("/activity-history", response_model=ActivityHistoryListOut, summary="Histórico de atividades")
@_erro_500("Erro ao consultar histórico de atividades")
def get_activity_history(
    auditoria: Auditoria,
    username: Optional[str] = Query(None, description="Filtrar por usuário"),
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    days: int = Query(7, description="Últimos N dias", ge=1, le=365),
    limit: int = Query(100, description="Limite de registros", ge=1, le=1000),
):
    historico = auditoria.historico_de_atividades(username, action, agora() - timedelta(days=days), limit)
    items = [
        {
            "id": item.id,
            "username": item.username,
            "action": item.action,
            "target_user": item.target_user,
            "details": item.details,
            "timestamp": item.timestamp,
            "ip_address": item.ip_address,
            "status": item.status,
        }
        for item in historico
    ]
    return {"total": len(items), "period_days": days, "items": items}


@router.get("/historico/{login}", response_model=UserHistoryListOut,
            summary="Histórico detalhado (linha do tempo) de um usuário específico")
@_erro_500("Erro ao consultar histórico do usuário")
def get_user_history(
    auditoria: Auditoria,
    login: str,
    limit: int = Query(100, description="Máximo de eventos retornados", ge=1, le=500),
):
    """
    Todos os eventos de um usuário (logins, logouts e atividades) numa única linha do tempo, do
    mais recente para o mais antigo. Útil para investigar "o que aconteceu com a conta de fulano".
    """
    eventos = auditoria.linha_do_tempo(login, limit)
    return {"total": len(eventos), "login": login, "items": eventos}


@router.get("/user-summary/{username}", summary="Resumo de atividades de um usuário")
@_erro_500("Erro ao consultar resumo do usuário")
def get_user_activity_summary(
    auditoria: Auditoria,
    username: str,
    days: int = Query(30, description="Últimos N dias", ge=1, le=365),
):
    """Resumo agregado (não é lista paginável, então não usa o envelope total/items)."""
    return auditoria.resumo_do_usuario(username, days)


@router.get("/security-report", summary="Relatório de segurança")
@_erro_500("Erro ao gerar relatório de segurança")
def get_security_report(
    auditoria: Auditoria,
    days: int = Query(7, description="Últimos N dias", ge=1, le=365),
):
    """Relatório agregado das falhas de login e dos IPs suspeitos (não é lista paginável)."""
    return auditoria.relatorio_de_seguranca(days)
