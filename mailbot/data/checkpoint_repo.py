"""Checkpoint repository for email processing state."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import aiosqlite
from loguru import logger

from mailbot.models.checkpoint import CheckpointModel


class CheckpointRepo(ABC):
    """Abstract checkpoint repository interface."""

    @abstractmethod
    async def get_checkpoint(self, email: str, mailbox: str) -> Optional[CheckpointModel]:
        """Get checkpoint or None if not found."""
        pass
    
    @abstractmethod
    async def save_checkpoint(self, checkpoint: CheckpointModel) -> None:
        """Save or update checkpoint."""
        pass

class RepositoryError(Exception):
    """Exception raised for repository operation errors."""
    pass


class SqliteCheckpointRepo(CheckpointRepo):
    """SQLite checkpoint repository."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
        logger.info(f"Initialized SQLite repository: {db_path}")

    async def __aenter__(self) -> "SqliteCheckpointRepo":
        try:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.row_factory = aiosqlite.Row
            await self._initialize_tables()
            logger.info("Database connected")
            return self
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise RepositoryError(f"Database connection failed: {e}") from e
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._connection:
            try:
                await self._connection.close()
                logger.info("Database closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self._connection = None
    
    async def _initialize_tables(self) -> None:
        try:
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    email TEXT NOT NULL,
                    mailbox TEXT NOT NULL,
                    uidvalidity INTEGER NOT NULL,
                    last_uid INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (email, mailbox)
                )
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_checkpoints_updated 
                ON checkpoints(updated_at)
            """)
            
            await self._connection.commit()
            logger.debug("Tables initialized")
        except Exception as e:
            logger.error(f"Table init failed: {e}")
            raise RepositoryError(f"Table initialization failed: {e}") from e

    async def get_checkpoint(self, email: str, mailbox: str) -> Optional[CheckpointModel]:
        if not self._connection:
            raise RepositoryError("Database connection not established")
            
        try:
            async with self._connection.execute(
                "SELECT email, mailbox, uidvalidity, last_uid, updated_at "
                "FROM checkpoints WHERE email = ? AND mailbox = ?",
                (email, mailbox)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row is None:
                    return None
                
                return CheckpointModel(
                    email=row["email"],
                    mailbox=row["mailbox"],
                    uidvalidity=row["uidvalidity"],
                    last_uid=row["last_uid"],
                    updated_at=row["updated_at"]
                )
                
        except Exception as e:
            logger.error(f"Get checkpoint failed: {e}")
            raise RepositoryError(f"Get checkpoint failed: {e}") from e

    async def save_checkpoint(self, checkpoint: CheckpointModel) -> None:
        if not self._connection:
            raise RepositoryError("Database connection not established")
            
        try:
            await self._connection.execute(
                """
                REPLACE INTO checkpoints 
                (email, mailbox, uidvalidity, last_uid, updated_at) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    checkpoint.email,
                    checkpoint.mailbox,
                    checkpoint.uidvalidity,
                    checkpoint.last_uid
                )
            )
            
            await self._connection.commit()
            logger.info(f"Saved checkpoint: {checkpoint.email}/{checkpoint.mailbox}")
            
        except Exception as e:
            logger.error(f"Save failed: {e}")
            await self._connection.rollback()
            raise RepositoryError(f"Save checkpoint failed: {e}") from e