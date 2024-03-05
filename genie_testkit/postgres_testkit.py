from typing import Optional

from genie_common.tools import logger
from genie_common.utils import random_alphanumeric_string
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer


class PostgresTestkit:
    def __init__(self,
                 container: Optional[PostgresContainer] = None,
                 image: Optional[str] = None,
                 port: Optional[int] = None,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 dbname: Optional[str] = None):
        self.image = image or "postgres:15.6"
        self.port = port or 5432
        self.user = user or random_alphanumeric_string()
        self.password = password or random_alphanumeric_string()
        self.dbname = dbname or random_alphanumeric_string()
        self._container = container

    def get_database_engine(self, driver: str = "asyncpg") -> AsyncEngine:
        raw_url = self._container.get_connection_url()
        url = raw_url.replace("psycopg2", driver)

        return create_async_engine(url=url, poolclass=NullPool)

    def __enter__(self) -> "PostgresTestkit":
        if self._container is None:
            logger.info("Starting Postgres container")
            self._container = PostgresContainer(
                image=self.image,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname,
                driver="psycopg2"
            )
            self._container.__enter__()

        else:
            logger.warn("Container already running. Ignoring request to start.")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._container is not None:
            self._container.__exit__(exc_type, exc_val, exc_tb)
