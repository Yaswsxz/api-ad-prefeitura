"""Auditoria: ações administrativas em duas fases e consulta do histórico."""
import json
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Iterator, Optional, TypeVar

from fastapi import HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.core.caminhos import com_sufixo_do_mes
from app.core.config import settings
from app.core.contexto import Contexto
from app.core.erros_ad import Codigo, ErroDominio
from app.core.logging_config import logger, request_id_var
from app.database import ActivityHistory, LoginHistory, SessionLocal, agora
from app.schemas.user import EventoLogin

# Estados de uma ação auditada: nasce INICIADA (intenção, antes de escrever no AD) e termina em
# um dos outros três.
STATUS_INTENCAO = "INICIADA"
STATUS_SUCESSO = "SUCCESS"
STATUS_FALHA = "FAILED"
STATUS_INCONSISTENTE = "INCONSISTENTE"   # algo ficou pela metade no AD (a compensação falhou)

LIMITE_TENTATIVAS_SUSPEITAS = 5   # falhas de login de um mesmo IP que o tornam suspeito

R = TypeVar("R")


class Acao(str, Enum):
    """Ações administrativas auditadas; o texto é o que fica gravado em activity_history.action."""
    CRIAR_UNIDADE = "CREATE_OU"
    ALTERAR_UNIDADE = "UPDATE_OU"
    DESINCORPORAR_UNIDADE = "DESINCORPORAR_OU"
    REINCORPORAR_UNIDADE = "REINCORPORAR_OU"
    CRIAR_HUMANO = "CREATE_HUMANO"
    CRIAR_NAO_HUMANO = "CREATE_NAO_HUMANO"
    ALTERAR_IDENTIDADE = "UPDATE_IDENTIDADE"
    BLOQUEAR_IDENTIDADE = "BLOCK_IDENTIDADE"
    DESBLOQUEAR_IDENTIDADE = "UNBLOCK_IDENTIDADE"
    DESTITUIR_IDENTIDADE = "DESTITUIR_IDENTIDADE"
    ATIVAR_IDENTIDADE = "ATIVAR_IDENTIDADE"
    TRANSFERIR_IDENTIDADE = "TRANSFERIR_IDENTIDADE"
    REDEFINIR_SENHA = "REDEFINIR_SENHA"
    REMOVER_IDENTIDADE = "DELETE_IDENTIDADE"


# =============================================================================
# Auditoria em duas fases
# =============================================================================

class Registro:
    """
    Uma ação administrativa em auditoria. Fase 1 (`abrir`): registra a intenção ANTES de escrever
    no AD; se não conseguir, levanta erro e a operação não ocorre. Fase 2 (`fechar`): registra o
    resultado; se não conseguir, o AD já mudou, então o fato vai para o arquivo de contingência.
    """

    def __init__(self, ctx: Contexto, acao: Acao, alvo: str, detalhes: dict[str, Any]):
        self.ctx, self.acao, self.alvo = ctx, acao, alvo
        self.detalhes: dict[str, Any] = dict(detalhes)
        self.inconsistente = False
        self._id: Optional[int] = None

    def _detalhes_completos(self) -> dict[str, Any]:
        if self.ctx.administrador:      # informado pelo cliente, não verificado
            return {**self.detalhes, "administrador": self.ctx.administrador}
        return self.detalhes

    def _json(self) -> Optional[str]:
        detalhes = self._detalhes_completos()
        return json.dumps(detalhes, ensure_ascii=False, default=str) if detalhes else None

    def abrir(self) -> None:
        try:
            with SessionLocal() as db:
                linha = ActivityHistory(
                    username=self.ctx.operador, action=self.acao.value,
                    target_user=self.alvo or self.ctx.operador, details=self._json(),
                    ip_address=self.ctx.ip, user_agent=self.ctx.user_agent,
                    status=STATUS_INTENCAO, timestamp=agora(),
                )
                db.add(linha)
                db.commit()
                self._id = linha.id
        except Exception as e:
            logger.error(f"AUDITORIA_INDISPONIVEL: intenção de {self.acao.value} não registrada ({type(e).__name__})")
            raise ErroDominio(
                "Não foi possível registrar a auditoria; a operação não foi executada.",
                codigo=Codigo.AUDITORIA_INDISPONIVEL, status_code=503,
            ) from e

    def fechar(self, status: str) -> None:
        """Nunca levanta erro: o AD pode já ter mudado."""
        try:
            with SessionLocal() as db:
                linha = db.get(ActivityHistory, self._id)
                linha.status, linha.details = status, self._json()
                db.commit()
        except Exception as e:
            logger.error(
                f"INCONSISTENTE: resultado da auditoria não registrado ({self.acao.value}, {status}; "
                f"{type(e).__name__}); fato gravado no arquivo de contingência")
            self._contingencia(status)

    def _contingencia(self, status: str) -> None:
        linha = json.dumps({
            "quando": agora().isoformat(), "request_id": request_id_var.get(),
            "operador": self.ctx.operador, "ip": self.ctx.ip, "acao": self.acao.value, "alvo": self.alvo,
            "status": status, "detalhes": self._detalhes_completos(),
        }, ensure_ascii=False, default=str)
        try:
            destino = com_sufixo_do_mes(settings.arquivo_contingencia, agora())    # um arquivo por mês, só acrescenta
            destino.parent.mkdir(parents=True, exist_ok=True)
            with open(destino, "a", encoding="utf-8") as arquivo:
                arquivo.write(linha + "\n")
        except Exception as e:
            logger.critical(f"AUDITORIA_PERDIDA (contingência indisponível: {type(e).__name__}): {linha}")


_registro_atual: ContextVar[Optional[Registro]] = ContextVar("registro_de_auditoria", default=None)


def marcar_inconsistente() -> None:
    """Chamado quando uma compensação falha: a ação em curso termina como INCONSISTENTE."""
    registro = _registro_atual.get()
    if registro is not None:
        registro.inconsistente = True


def _descrever_erro(e: Exception) -> dict[str, Any]:
    if isinstance(e, ErroDominio):
        return {"erro": e.codigo, "status_http": e.status_code}
    if isinstance(e, HTTPException):
        return {"erro": f"HTTP_{e.status_code}", "status_http": e.status_code}
    return {"erro": type(e).__name__}


@contextmanager
def auditar(ctx: Contexto, acao: Acao, alvo: str, **detalhes: Any) -> Iterator[Registro]:
    """
    Envolve uma operação de escrita: abre a intenção (bloqueante), executa e fecha com o resultado
    (sucesso ou falha). Sucessos e falhas são registrados; leituras não passam por aqui.
    """
    registro = Registro(ctx, acao, alvo, detalhes)
    registro.abrir()
    marca = _registro_atual.set(registro)
    try:
        yield registro
    except Exception as e:
        registro.detalhes.update(_descrever_erro(e))
        registro.fechar(STATUS_INCONSISTENTE if registro.inconsistente else STATUS_FALHA)
        raise
    else:
        registro.fechar(STATUS_INCONSISTENTE if registro.inconsistente else STATUS_SUCESSO)
    finally:
        _registro_atual.reset(marca)


def executar_auditado(ctx: Contexto, acao: Acao, alvo: str, inicial: dict[str, Any],
                      operacao: Callable[[], tuple[R, dict[str, Any]]]) -> R:
    """
    Roda `operacao`, que devolve (resultado, detalhes finais), dentro de `auditar`. Os detalhes
    iniciais são os da intenção; os finais são acrescentados ao registrar o resultado.
    """
    with auditar(ctx, acao, alvo, **inicial) as registro:
        resultado, detalhes = operacao()
        registro.detalhes.update(detalhes)
    return resultado


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    # --- escrita -----------------------------------------------------------

    def _gravar(self, registro, descricao: str) -> None:
        try:
            self.db.add(registro)
            self.db.commit()
        except Exception as e:
            logger.error(f"Erro ao registrar {descricao}: {e}")
            self.db.rollback()

    def registrar_login(self, username: str, ip_address: Optional[str], user_agent: Optional[str],
                        sucesso: bool = True, mensagem_erro: Optional[str] = None) -> None:
        self._gravar(LoginHistory(
            username=username, event_type=EventoLogin.LOGIN.value, ip_address=ip_address,
            user_agent=user_agent, success=sucesso, error_message=mensagem_erro, timestamp=agora(),
        ), "login")

    # --- consulta ----------------------------------------------------------

    def historico_de_logins(self, username: Optional[str] = None, start_date: Optional[datetime] = None,
                            limit: int = 100) -> list[LoginHistory]:
        query = self.db.query(LoginHistory)
        if username:
            query = query.filter(LoginHistory.username == username)
        if start_date:
            query = query.filter(LoginHistory.timestamp >= start_date)
        return query.order_by(LoginHistory.timestamp.desc()).limit(limit).all()

    def historico_de_atividades(self, username: Optional[str] = None, action: Optional[str] = None,
                                start_date: Optional[datetime] = None, limit: int = 100) -> list[ActivityHistory]:
        query = self.db.query(ActivityHistory)
        if username:
            query = query.filter(
                (ActivityHistory.username == username) | (ActivityHistory.target_user == username)
            )
        if action:
            query = query.filter(ActivityHistory.action == action)
        if start_date:
            query = query.filter(ActivityHistory.timestamp >= start_date)
        return query.order_by(ActivityHistory.timestamp.desc()).limit(limit).all()

    def listar_logins(self, username: Optional[str] = None, event_type: Optional[str] = None,
                      sucesso: Optional[bool] = None, data_inicio: Optional[datetime] = None,
                      data_fim: Optional[datetime] = None, ordenar_por: str = "timestamp",
                      ordem: str = "desc", limite: int = 100) -> list[LoginHistory]:
        """Logins/logouts com filtros (`username` casa por parte do nome) e ordenação."""
        query = self.db.query(LoginHistory)
        if username:
            query = query.filter(LoginHistory.username.ilike(f"%{username}%"))
        if event_type:
            query = query.filter(LoginHistory.event_type == event_type)
        if sucesso is not None:
            query = query.filter(LoginHistory.success == sucesso)
        if data_inicio:
            query = query.filter(LoginHistory.timestamp >= data_inicio)
        if data_fim:
            query = query.filter(LoginHistory.timestamp <= data_fim)
        coluna = getattr(LoginHistory, ordenar_por, LoginHistory.timestamp)
        return query.order_by(desc(coluna) if ordem.lower() == "desc" else asc(coluna)).limit(limite).all()

    def linha_do_tempo(self, username: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Logins/logouts e atividades de um usuário numa única lista, do mais recente ao mais antigo.
        Cada evento tem o mesmo formato, venha de LoginHistory ou de ActivityHistory.
        """
        eventos = [
            {"tipo": l.event_type, "timestamp": l.timestamp, "sucesso": bool(l.success),
             "ip_address": l.ip_address, "detalhes": l.error_message}
            for l in self.historico_de_logins(username=username, limit=limit)
        ] + [
            {"tipo": a.action, "timestamp": a.timestamp, "sucesso": a.status == STATUS_SUCESSO,
             "ip_address": a.ip_address, "detalhes": a.details}
            for a in self.historico_de_atividades(username=username, limit=limit)
        ]
        eventos.sort(key=lambda e: e["timestamp"], reverse=True)
        return eventos[:limit]

    def resumo_do_usuario(self, username: str, days: int = 30) -> dict[str, Any]:
        desde = agora() - timedelta(days=days)

        def contar_logins(sucesso: bool) -> int:
            return self.db.query(LoginHistory).filter(
                LoginHistory.username == username,
                LoginHistory.event_type == EventoLogin.LOGIN.value,
                LoginHistory.timestamp >= desde,
                LoginHistory.success == sucesso,
            ).count()

        atividades = self.db.query(ActivityHistory.action, ActivityHistory.status).filter(
            (ActivityHistory.username == username) | (ActivityHistory.target_user == username),
            ActivityHistory.timestamp >= desde,
        ).all()
        contagem: dict[str, dict[str, int]] = {}
        for action, status in atividades:
            c = contagem.setdefault(action, {"total": 0, "success": 0, "failed": 0})
            c["total"] += 1
            c["success" if status == STATUS_SUCESSO else "failed"] += 1

        return {
            "username": username,
            "period_days": days,
            "total_logins": contar_logins(True),
            "failed_logins": contar_logins(False),
            "total_activities": len(atividades),
            "action_counts": contagem,
        }

    def relatorio_de_seguranca(self, days: int) -> dict[str, Any]:
        """Falhas de login no período e os IPs com muitas tentativas."""
        desde = agora() - timedelta(days=days)
        falhas = [l for l in self.historico_de_logins(start_date=desde, limit=1000) if not l.success]
        por_ip: dict[str, list[LoginHistory]] = {}
        for falha in falhas:
            por_ip.setdefault(falha.ip_address or "unknown", []).append(falha)
        return {
            "period_days": days,
            "total_failed_logins": len(falhas),
            "suspicious_ips": {
                ip: {
                    "attempts": len(tentativas),
                    "first_attempt": min(t.timestamp for t in tentativas).isoformat(),
                    "last_attempt": max(t.timestamp for t in tentativas).isoformat(),
                }
                for ip, tentativas in por_ip.items()
                if len(tentativas) >= LIMITE_TENTATIVAS_SUSPEITAS
            },
        }
