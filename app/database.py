from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# URL de conexão com o SQLite (pode vir do .env, mas tem fallback local)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ad_audit.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class LoginHistory(Base):
    """
    Tabela que registra todas as tentativas de login/logout no sistema.
    Essencial para auditoria de acessos e segurança (LGPD).
    """
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    event_type = Column(String(20), nullable=False)  # 'login' ou 'logout'
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Índices compostos para melhorar performance em consultas frequentes
    __table_args__ = (
        Index('idx_login_username_time', 'username', 'timestamp'),
    )


class ActivityHistory(Base):
    """
    Tabela que registra todas as ações administrativas realizadas na API.
    Exemplos: criação, edição, exclusão, troca de senha, habilitação/desabilitação.
    """
    __tablename__ = "activity_history"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    target_user = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(20), default="SUCCESS")

    __table_args__ = (
        Index('idx_activity_username_time', 'username', 'timestamp'),
        Index('idx_activity_action', 'action'),
    )

Base.metadata.create_all(bind=engine)


def get_db():
    """Gerenciador de sessão para o SQLAlchemy (dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()