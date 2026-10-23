from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text, create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.caminhos import resolver
from app.core.config import settings


def url_do_banco(url: str) -> URL:
    """
    URL do banco de auditoria. SQLite em arquivo é resolvido a partir da raiz do projeto (não do
    diretório corrente) e o diretório é criado.
    """
    u = make_url(url)
    if u.get_backend_name() == "sqlite" and u.database and u.database != ":memory:":
        arquivo = resolver(u.database)
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        u = u.set(database=str(arquivo))
    return u


DATABASE_URL = url_do_banco(settings.database_url)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.get_backend_name() == "sqlite" else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def agora() -> datetime:
    """Instante atual em UTC, sem fuso (é como as colunas de data guardam)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class LoginHistory(Base):
    """Tentativas de login/logout (auditoria de acessos e segurança, LGPD)."""
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    event_type = Column(String(20), nullable=False)  # 'login' ou 'logout'
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    timestamp = Column(DateTime, default=agora, index=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_login_username_time', 'username', 'timestamp'),
    )


class ActivityHistory(Base):
    """Ações administrativas realizadas na API (criação, alteração, destituição etc.)."""
    __tablename__ = "activity_history"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    target_user = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    timestamp = Column(DateTime, default=agora, index=True)
    status = Column(String(20), default="SUCCESS")

    __table_args__ = (
        Index('idx_activity_username_time', 'username', 'timestamp'),
        Index('idx_activity_action', 'action'),
    )


def iniciar_banco() -> None:
    """Cria as tabelas de auditoria que ainda não existem."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Gerenciador de sessão para o SQLAlchemy (dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
