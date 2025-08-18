#!/usr/bin/env python3
"""Example demonstrating checkpoint repository factory usage.

This example shows different ways to use the CheckpointRepoFactory
for creating repository instances with proper dependency injection.
"""

import asyncio
from pathlib import Path

from mailbot.config.config import get_settings
from mailbot.data import CheckpointRepoFactory, create_checkpoint_repo
from mailbot.models.checkpoint import CheckpointModel


async def example_using_config():
    """Example using configuration-driven factory with actual DatabaseConfig."""
    print("=== Example 1: Using Actual DatabaseConfig ===")
    
    # Get application settings (which include DatabaseConfig)
    settings = get_settings()
    
    # Create repository using factory with actual DatabaseConfig
    # No protocols or wrappers needed - uses the real config class!
    repo = CheckpointRepoFactory.create_checkpoint_repo(settings.database)
    
    async with repo as db_repo:
        # Example checkpoint
        checkpoint = CheckpointModel(
            email="user@example.com",
            mailbox="INBOX",
            uidvalidity=12345,
            last_uid=100
        )
        
        # Save checkpoint
        await db_repo.save_checkpoint(checkpoint)
        print(f"Saved checkpoint: {checkpoint}")
        
        # Retrieve checkpoint
        retrieved = await db_repo.get_checkpoint("user@example.com", "INBOX")
        print(f"Retrieved checkpoint: {retrieved}")


async def example_using_convenience_function():
    """Example using convenience function."""
    print("\n=== Example 2: Using Convenience Function ===")
    
    # Create repository using convenience function
    repo = create_checkpoint_repo(
        database_type="sqlite",
        database_path=Path("./examples/example_checkpoints.db")
    )
    
    async with repo as db_repo:
        # Example checkpoint
        checkpoint = CheckpointModel(
            email="another@example.com",
            mailbox="Sent",
            uidvalidity=67890,
            last_uid=50
        )
        
        # Save checkpoint
        await db_repo.save_checkpoint(checkpoint)
        print(f"Saved checkpoint: {checkpoint}")
        
        # Retrieve checkpoint
        retrieved = await db_repo.get_checkpoint("another@example.com", "Sent")
        print(f"Retrieved checkpoint: {retrieved}")


async def example_direct_factory_usage():
    """Example using factory directly."""
    print("\n=== Example 3: Direct Factory Usage ===")
    
    # Create repository using factory directly
    db_path = Path("./examples/direct_example.db")
    repo = CheckpointRepoFactory.create_sqlite_checkpoint_repo(db_path)
    
    async with repo as db_repo:
        # Example checkpoint
        checkpoint = CheckpointModel(
            email="direct@example.com",
            mailbox="Drafts",
            uidvalidity=11111,
            last_uid=25
        )
        
        # Save checkpoint
        await db_repo.save_checkpoint(checkpoint)
        print(f"Saved checkpoint: {checkpoint}")
        
        # Retrieve checkpoint
        retrieved = await db_repo.get_checkpoint("direct@example.com", "Drafts")
        print(f"Retrieved checkpoint: {retrieved}")


async def main():
    """Run all examples."""
    try:
        await example_using_config()
        await example_using_convenience_function()
        await example_direct_factory_usage()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        raise


if __name__ == "__main__":
    # Create examples directory
    Path("./examples").mkdir(exist_ok=True)
    
    # Run examples
    asyncio.run(main())
