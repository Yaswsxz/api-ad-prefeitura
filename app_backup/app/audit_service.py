from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
from app.database import LoginHistory, ActivityHistory
import logging

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def log_login(self, username: str, ip_address: str, user_agent: str, 
                  success: bool = True, error_message: str = None):
        try:
            login_log = LoginHistory(
                username=username,
                event_type="login",
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message,
                timestamp=datetime.utcnow()
            )
            self.db.add(login_log)
            self.db.commit()
        except Exception as e:
            logger.error(f"Erro ao registrar login: {e}")
            self.db.rollback()
    
    def log_logout(self, username: str, ip_address: str, user_agent: str):
        try:
            logout_log = LoginHistory(
                username=username,
                event_type="logout",
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                timestamp=datetime.utcnow()
            )
            self.db.add(logout_log)
            self.db.commit()
        except Exception as e:
            logger.error(f"Erro ao registrar logout: {e}")
            self.db.rollback()
    
    def log_activity(self, username: str, action: str, target_user: Optional[str] = None,
                     details: Optional[Dict[str, Any]] = None, 
                     ip_address: Optional[str] = None, 
                     user_agent: Optional[str] = None,
                     status: str = "SUCCESS"):
        try:
            activity = ActivityHistory(
                username=username,
                action=action,
                target_user=target_user or username,
                details=json.dumps(details, ensure_ascii=False) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                timestamp=datetime.utcnow()
            )
            self.db.add(activity)
            self.db.commit()
        except Exception as e:
            logger.error(f"Erro ao registrar atividade: {e}")
            self.db.rollback()
    
    def get_login_history(self, username: Optional[str] = None, 
                          start_date: Optional[datetime] = None,
                          limit: int = 100) -> List[LoginHistory]:
        query = self.db.query(LoginHistory)
        if username:
            query = query.filter(LoginHistory.username == username)
        if start_date:
            query = query.filter(LoginHistory.timestamp >= start_date)
        return query.order_by(LoginHistory.timestamp.desc()).limit(limit).all()
    
    def get_activity_history(self, username: Optional[str] = None,
                             action: Optional[str] = None,
                             start_date: Optional[datetime] = None,
                             limit: int = 100) -> List[ActivityHistory]:
        query = self.db.query(ActivityHistory)
        if username:
            query = query.filter(
                (ActivityHistory.username == username) | 
                (ActivityHistory.target_user == username)
            )
        if action:
            query = query.filter(ActivityHistory.action == action)
        if start_date:
            query = query.filter(ActivityHistory.timestamp >= start_date)
        return query.order_by(ActivityHistory.timestamp.desc()).limit(limit).all()
    
    def get_user_activity_summary(self, username: str, days: int = 30) -> Dict[str, Any]:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        logins = self.db.query(LoginHistory).filter(
            LoginHistory.username == username,
            LoginHistory.event_type == "login",
            LoginHistory.timestamp >= since_date,
            LoginHistory.success == True
        ).count()
        
        failed_logins = self.db.query(LoginHistory).filter(
            LoginHistory.username == username,
            LoginHistory.event_type == "login",
            LoginHistory.timestamp >= since_date,
            LoginHistory.success == False
        ).count()
        
        activities = self.db.query(ActivityHistory.action, 
                                   ActivityHistory.status).filter(
            (ActivityHistory.username == username) | 
            (ActivityHistory.target_user == username),
            ActivityHistory.timestamp >= since_date
        ).all()
        
        action_counts = {}
        for action, status in activities:
            if action not in action_counts:
                action_counts[action] = {"total": 0, "success": 0, "failed": 0}
            action_counts[action]["total"] += 1
            if status == "SUCCESS":
                action_counts[action]["success"] += 1
            else:
                action_counts[action]["failed"] += 1
        
        return {
            "username": username,
            "period_days": days,
            "total_logins": logins,
            "failed_logins": failed_logins,
            "total_activities": len(activities),
            "action_counts": action_counts
        }