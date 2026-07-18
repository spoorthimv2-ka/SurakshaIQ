import logging
from typing import AsyncGenerator
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config.settings import settings

logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self._driver: AsyncDriver | None = None

    async def connect(self):
        if settings.neo4j_uri and settings.neo4j_user and settings.neo4j_password:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password)
                )
                await self._driver.verify_connectivity()
                logger.info("Connected to Neo4j successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {str(e)}")
                self._driver = None
        else:
            logger.warning("Neo4j connection details missing. Graph functionality will be limited.")

    async def close(self):
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j connection closed.")

    @property
    def driver(self) -> AsyncDriver | None:
        return self._driver

neo4j_conn = Neo4jConnection()

async def get_neo4j_session() -> AsyncGenerator:
    if not neo4j_conn.driver:
        yield None
        return
        
    async with neo4j_conn.driver.session() as session:
        yield session
