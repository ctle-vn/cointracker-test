import os
import logging
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session

from db.models.base import Base
import os
from dotenv import load_dotenv

# XXX: This is needed for alembic to detect the models
import db.models.models

load_dotenv()  # This loads the environment variables from .env file

# Load environment variables
# POSTGRES_USER = os.getenv("POSTGRES_USER")
# POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
# POSTGRES_DB = os.getenv("POSTGRES_DB")

url = sa.engine.URL.create(
    drivername="postgresql+psycopg2",
    username="admin",
    password="password",
    database="dev_db",
    host="db",
    # host="localhost",  # use this when you need to run migrations locally via: alembic revision --autogenerate -m "some message"
    port="5432",
)
engine = sa.create_engine(
    url=url,
    future=True,
)
Session = scoped_session(sessionmaker(engine, expire_on_commit=False))
logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
# Uncomment to see SQL statements logged.
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
