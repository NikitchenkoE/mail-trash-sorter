"""Repository factory for checkpoint repositories."""

from pathlib import Path
from typing import Literal

from loguru import logger

from mailbot.config.config import DatabaseConfig
from mailbot.data.checkpoint_repo import CheckpointRepo, SqliteCheckpointRepo


class RepositoryFactoryError(Exception):
    """Repository factory error."""
    pass


class CheckpointRepoFactory:
    """Factory for checkpoint repositories."""
    
    @staticmethod
    def create_checkpoint_repo(config: DatabaseConfig) -> CheckpointRepo:
        """Create repository based on config."""
        logger.info(f"Creating {config.database_type} repository")
        
        try:
            if config.database_type == "sqlite":
                return CheckpointRepoFactory.create_sqlite_checkpoint_repo(
                    config.database_path
                )
            elif config.database_type == "dynamodb":
                raise RepositoryFactoryError("DynamoDB not yet implemented")
            else:
                raise RepositoryFactoryError(f"Unsupported type: {config.database_type}")
                
        except Exception as e:
            logger.error(f"Repository creation failed: {e}")
            raise RepositoryFactoryError(f"Creation failed: {e}") from e
    
    @staticmethod
    def create_sqlite_checkpoint_repo(db_path: Path) -> SqliteCheckpointRepo:
        """Create SQLite repository."""
        if not isinstance(db_path, Path):
            db_path = Path(db_path)
            
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return SqliteCheckpointRepo(db_path)
        except Exception as e:
            logger.error(f"SQLite creation failed: {e}")
            raise RepositoryFactoryError(f"SQLite creation failed: {e}") from e
    
    @staticmethod
    def create_dynamodb_checkpoint_repo() -> CheckpointRepo:
        """Create DynamoDB repository (not implemented)."""
        raise RepositoryFactoryError("DynamoDB not implemented")


def create_checkpoint_repo(
    database_type: Literal["sqlite", "dynamodb"] = "sqlite",
    database_path: Path = Path("./data/checkpoints.db")
) -> CheckpointRepo:
    """Convenience function for creating repositories."""
    if database_type == "sqlite":
        return CheckpointRepoFactory.create_sqlite_checkpoint_repo(database_path)
    elif database_type == "dynamodb":
        return CheckpointRepoFactory.create_dynamodb_checkpoint_repo()
    else:
        raise RepositoryFactoryError(f"Unsupported type: {database_type}")
