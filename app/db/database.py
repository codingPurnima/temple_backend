from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings


engine=create_engine(settings.DATABASE_URL, echo= True, pool_pre_ping=True, connect_args={
    "charset": "utf8mb4",
    "use_unicode": True
})

@event.listens_for(engine, "connect")
def set_mysql_encoding(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.close()

@event.listens_for(engine, "connect")
def set_names(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.close()
    
SessionLocal= sessionmaker(autoflush=False, bind=engine)

Base= declarative_base()
