#!/usr/bin/env python3
"""Examples demonstrating dependency injection patterns vs. direct imports.

This example shows the difference between proper dependency injection
and tightly coupled code that imports dependencies directly.
"""

import asyncio
from pathlib import Path

from mailbot.config.config import DatabaseConfig, get_settings
from mailbot.data import CheckpointRepoFactory
from mailbot.models.checkpoint import CheckpointModel


class EmailProcessor:
    """Example service that processes emails and needs a checkpoint repository."""
    
    def __init__(self, checkpoint_repo_factory: CheckpointRepoFactory, 
                 database_config: DatabaseConfig) -> None:
        """Initialize with dependency injection.
        
        Args:
            checkpoint_repo_factory: Factory for creating repositories
            database_config: Database configuration
        """
        self.repo_factory = checkpoint_repo_factory
        self.database_config = database_config
        
    async def process_emails(self, email_account: str) -> None:
        """Process emails for an account using injected dependencies."""
        print(f"Processing emails for {email_account}")
        
        # Use injected factory and config
        repo = self.repo_factory.create_checkpoint_repo(self.database_config)
        
        async with repo as checkpoint_repo:
            # Get last checkpoint
            checkpoint = await checkpoint_repo.get_checkpoint(email_account, "INBOX")
            
            if checkpoint:
                print(f"Resuming from UID {checkpoint.last_uid}")
            else:
                print("Starting fresh - no previous checkpoint")
                checkpoint = CheckpointModel(
                    email=email_account,
                    mailbox="INBOX", 
                    uidvalidity=12345,
                    last_uid=0
                )
            
            # Simulate processing some emails
            checkpoint.last_uid += 10
            await checkpoint_repo.save_checkpoint(checkpoint)
            print(f"Saved checkpoint at UID {checkpoint.last_uid}")


class EmailProcessorBadExample:
    """BAD EXAMPLE: Tightly coupled - imports dependencies directly."""
    
    def __init__(self) -> None:
        """No dependencies injected - will import them directly."""
        pass
        
    async def process_emails(self, email_account: str) -> None:
        """BAD: Imports dependencies directly inside the method."""
        print(f"[BAD] Processing emails for {email_account}")
        
        # BAD: Direct imports make this hard to test and configure
        from mailbot.config.config import get_settings
        from mailbot.data import CheckpointRepoFactory
        
        settings = get_settings()  # Hard to mock
        factory = CheckpointRepoFactory()  # Hard to replace
        repo = factory.create_checkpoint_repo(settings.database)  # Fixed config
        
        # Rest of the logic...
        print("[BAD] This is tightly coupled and hard to test!")


async def example_dependency_injection():
    """GOOD EXAMPLE: Using dependency injection."""
    print("=== ✅ Good Example: Dependency Injection ===")
    
    # Load configuration at the application boundary
    settings = get_settings()
    
    # Create dependencies
    repo_factory = CheckpointRepoFactory()
    
    # Inject dependencies into the service
    processor = EmailProcessor(
        checkpoint_repo_factory=repo_factory,
        database_config=settings.database
    )
    
    # Use the service
    await processor.process_emails("user@example.com")
    print("✅ Easy to test - all dependencies are injectable!\n")


async def example_bad_pattern():
    """BAD EXAMPLE: Direct imports (tightly coupled)."""
    print("=== ❌ Bad Example: Direct Imports ===")
    
    # BAD: Service creates its own dependencies
    processor = EmailProcessorBadExample()
    await processor.process_emails("user@example.com")
    print("❌ Hard to test - dependencies are hardcoded!\n")


async def example_testing_benefits():
    """Show how dependency injection makes testing easier."""
    print("=== 🧪 Testing Benefits ===")
    
    # For testing, we can easily inject different configurations
    test_config = DatabaseConfig(
        database_type="sqlite",
        sqlite_db_path=Path("./test_checkpoints.db")
    )
    
    test_factory = CheckpointRepoFactory()
    
    # Same service, different dependencies for testing
    test_processor = EmailProcessor(
        checkpoint_repo_factory=test_factory,
        database_config=test_config
    )
    
    await test_processor.process_emails("test@example.com")
    print("🧪 Easy to test with different configurations!\n")


async def example_different_configs():
    """Show how easy it is to use different configurations."""
    print("=== 🔧 Different Configurations ===")
    
    # Configuration 1: Default SQLite
    config1 = DatabaseConfig(
        database_type="sqlite",
        sqlite_db_path=Path("./app_checkpoints.db")
    )
    
    # Configuration 2: Different SQLite file  
    config2 = DatabaseConfig(
        database_type="sqlite",
        sqlite_db_path=Path("./backup_checkpoints.db")
    )
    
    factory = CheckpointRepoFactory()
    
    # Same service, different databases
    processor1 = EmailProcessor(factory, config1)
    processor2 = EmailProcessor(factory, config2)
    
    await processor1.process_emails("main@example.com") 
    await processor2.process_emails("backup@example.com")
    
    print("🔧 Same code, different configurations!\n")


async def main():
    """Run all examples to show the patterns."""
    print("Dependency Injection Patterns Demo\n")
    
    try:
        await example_dependency_injection()
        await example_bad_pattern()
        await example_testing_benefits()
        await example_different_configs()
        
        print("🎉 All examples completed!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        raise


if __name__ == "__main__":
    # Create examples directory
    Path("./examples").mkdir(exist_ok=True)
    
    # Run examples
    asyncio.run(main())
