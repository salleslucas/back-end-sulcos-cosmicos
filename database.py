"""
database.py
---------------------------------------------------------------------------
Módulo de configuração da camada de persistência.

Responsável por estabelecer a conexão entre a aplicação e o banco de dados
SQLite por meio do ORM SQLAlchemy. A escolha pelo SQLite se justifica pelo
escopo acadêmico do projeto: trata-se de um banco embutido, sem necessidade
de servidor dedicado, adequado para prototipação e avaliação local.

O arquivo de banco de dados (`sulco_cosmico.db`) é gerado automaticamente na
raiz do projeto na primeira execução. Em ambiente conteinerizado (Docker),
o arquivo persiste no volume mapeado entre o container e o sistema de arquivos
do host, conforme configurado no `docker-compose.yml`.
---------------------------------------------------------------------------
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Caminho relativo ao diretório de execução da aplicação.
# A notação "sqlite:///./arquivo.db" instrui o SQLAlchemy a criar
# o banco no diretório corrente (raiz do projeto).
DATABASE_URL = "sqlite:///./sulco_cosmico.db"

engine = create_engine(
    DATABASE_URL,
    # O parâmetro check_same_thread=False é necessário para uso com FastAPI,
    # pois o framework utiliza múltiplas threads para processar requisições
    # concorrentes. Por padrão, o SQLite proíbe o compartilhamento de uma
    # mesma conexão entre threads distintas; esta flag desabilita essa restrição.
    connect_args={"check_same_thread": False},
)

# SessionLocal é a fábrica de sessões do SQLAlchemy.
# autocommit=False → as transações são confirmadas explicitamente via db.commit().
# autoflush=False  → alterações pendentes não são enviadas ao banco antes de
#                    cada consulta, o que oferece mais controle transacional.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    Classe base declarativa para todos os modelos ORM do projeto.

    Ao herdar desta classe, cada modelo registra sua tabela no metadata
    do SQLAlchemy, permitindo que `Base.metadata.create_all()` crie as
    tabelas automaticamente no banco de dados na inicialização da aplicação.
    """
    pass


def get_db():
    """
    Gerador utilizado como dependência nas rotas do FastAPI (Dependency Injection).

    Abre uma sessão de banco de dados por requisição e a encerra ao final,
    independentemente de a operação ter sido concluída com sucesso ou ter
    lançado uma exceção. O bloco `finally` garante que a sessão seja sempre
    liberada, evitando vazamento de conexões.

    Uso nas rotas:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
