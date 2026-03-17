"""
database.py
---------------------------------------------------------------------------
Configuração da conexão com o banco de dados SQLite via SQLAlchemy.

O arquivo `sulco_cosmico.db` é criado automaticamente na raiz do projeto
na primeira execução. Em ambiente Docker, persiste enquanto o container
existir (ou enquanto o volume estiver montado).
---------------------------------------------------------------------------
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# sqlite:///./sulco_cosmico.db  →  arquivo local na raiz do projeto
DATABASE_URL = "sqlite:///./sulco_cosmico.db"

engine = create_engine(
    DATABASE_URL,
    # check_same_thread=False é obrigatório para SQLite com FastAPI
    # (múltiplas threads podem acessar a mesma conexão)
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM."""
    pass


def get_db():
    """
    Dependency injection do FastAPI.
    Abre uma sessão por requisição e fecha ao final (mesmo em caso de erro).

    Uso nas rotas:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
