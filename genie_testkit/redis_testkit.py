from typing import Optional

from redis import Redis
from genie_common.tools import logger
from genie_common.utils import random_alphanumeric_string
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


class RedisTestkit:
    def __init__(self,
                 container: Optional[PostgresContainer] = None,
                 image: Optional[str] = None,
                 port: Optional[int] = None,
                 password: Optional[str] = None):
        self.image = image or "redis:7.2"
        self.port = port or 6379
        self.password = password or random_alphanumeric_string()
        self._container = container

    def get_redis(self) -> Redis:
        exposed_port: str = self._container.get_exposed_port(self.port)
        return Redis(
            host=self._container.get_container_host_ip(),
            port=int(exposed_port),
            password=self.password,
        )

    def __enter__(self) -> "RedisTestkit":
        if self._container is None:
            logger.info("Starting Redis container")
            self._container = RedisContainer(
                image=self.image,
                port_to_expose=self.port,
                password=self.password,
            )
            self._container.__enter__()
            self._container.with_kwargs()

        else:
            logger.warn("Container already running. Ignoring request to start.")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._container is not None:
            self._container.__exit__(exc_type, exc_val, exc_tb)
