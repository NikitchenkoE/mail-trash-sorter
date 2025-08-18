"""Data storage and management for the mail sorter."""

from mailbot.data.checkpoint_repo import CheckpointRepo, SqliteCheckpointRepo
from mailbot.data.repo_factory import CheckpointRepoFactory, create_checkpoint_repo

__all__ = [
    "CheckpointRepo",
    "SqliteCheckpointRepo", 
    "CheckpointRepoFactory",
    "create_checkpoint_repo",
]
