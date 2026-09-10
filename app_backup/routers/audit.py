from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db
from app.audit_service import AuditService

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])


@router.get("/login-history", summary="Histórico de logins/logouts")
def get_login_history(
    request: Request,
    username: Optional[str] = Query(None, description="Filtrar por usuário"),
    days: int = Query(7, description="Últimos N dias", ge=1, le=365),
    limit: int = Query(100, description="Limite de registros", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    try:
        audit_service = AuditService(db)
        start_date = datetime.utcnow() - timedelta(days=days)
        history = audit_service.get_login_history(username, start_date, limit)
        
        result = []
        for item in history:
            result.append({
                "id": item.id,
                "username": item.username,
                "event_type": item.event_type,
                "timestamp": item.timestamp.isoformat(),
                "ip_address": item.ip_address,
                "success": item.success,
                "error_message": item.error_message
            })
        
        return {
            "total": len(result),
            "period_days": days,
            "history": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity-history", summary="Histórico de atividades")
def get_activity_history(
    request: Request,
    username: Optional[str] = Query(None, description="Filtrar por usuário"),
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    days: int = Query(7, description="Últimos N dias", ge=1, le=365),
    limit: int = Query(100, description="Limite de registros", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    try:
        audit_service = AuditService(db)
        start_date = datetime.utcnow() - timedelta(days=days)
        history = audit_service.get_activity_history(username, action, start_date, limit)
        
        result = []
        for item in history:
            result.append({
                "id": item.id,
                "username": item.username,
                "action": item.action,
                "target_user": item.target_user,
                "details": item.details,
                "timestamp": item.timestamp.isoformat(),
                "ip_address": item.ip_address,
                "status": item.status
            })
        
        return {
            "total": len(result),
            "period_days": days,
            "history": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-summary/{username}", summary="Resumo de atividades de um usuário")
def get_user_activity_summary(
    request: Request,
    username: str,
    days: int = Query(30, description="Últimos N dias", ge=1, le=365),
    db: Session = Depends(get_db)
):
    try:
        audit_service = AuditService(db)
        return audit_service.get_user_activity_summary(username, days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security-report", summary="Relatório de segurança")
def get_security_report(
    request: Request,
    days: int = Query(7, description="Últimos N dias", ge=1, le=365),
    db: Session = Depends(get_db)
):
    try:
        audit_service = AuditService(db)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        failed_logins = audit_service.get_login_history(start_date=start_date, limit=1000)
        failed_logins = [l for l in failed_logins if not l.success]
        
        ip_attempts = {}
        for login in failed_logins:
            ip = login.ip_address or "unknown"
            if ip not in ip_attempts:
                ip_attempts[ip] = []
            ip_attempts[ip].append(login)
        
        suspicious_ips = {
            ip: attempts 
            for ip, attempts in ip_attempts.items() 
            if len(attempts) >= 5
        }
        
        return {
            "period_days": days,
            "total_failed_logins": len(failed_logins),
            "suspicious_ips": {
                ip: {
                    "attempts": len(attempts),
                    "first_attempt": min(a.timestamp for a in attempts).isoformat(),
                    "last_attempt": max(a.timestamp for a in attempts).isoformat()
                }
                for ip, attempts in suspicious_ips.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))