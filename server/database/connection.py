from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

SessionMaker = None
db_url = None


def get_session():
    global SessionMaker
    global db_url

    #    print("no")

    if SessionMaker == None:  # use , poolclass=NullPool for mysql and connect_args={'check_same_thread': False} for sqlite
        SessionMaker = sessionmaker(bind=create_engine(db_url),
                                    expire_on_commit=False, autoflush=False)
    return SessionMaker()


@contextmanager
def transaction():
    """Provide a transactional scope around a series of operations."""
    global SessionMaker
    global db_url

    # print("no")
    if SessionMaker == None:  # use , poolclass=NullPool for mysql and connect_args={'check_same_thread': False} for sqlite
        SessionMaker = sessionmaker(bind=create_engine(db_url),
                                    expire_on_commit=False, autoflush=False)
    session = SessionMaker()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()