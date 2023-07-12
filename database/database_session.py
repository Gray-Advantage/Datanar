from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from util import CONFIG

SqlAlchemyBase = declarative_base()
__factory: sessionmaker = None


def global_init() -> None:
    global __factory

    if __factory:
        return

    login = CONFIG["MySQL"]["database_login"]
    password = CONFIG["MySQL"]["database_password"]
    db_name = CONFIG["MySQL"]["database_name"]

    connect_link = f"mysql+mysqlconnector://{login}:{password}@localhost/{db_name}"

    engine = create_engine(connect_link, echo=False, pool_recycle=3600)

    __factory = sessionmaker(bind=engine)

    from database import __all_models
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    return __factory()
