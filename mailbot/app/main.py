"""Main entry point for the mail trash sorter application."""

import click
from loguru import logger

from mailbot.config.config import DatabaseConfig, Settings, get_settings
from mailbot.data import CheckpointRepoFactory


class MailTrashSorterApp:
    """Main application class with dependency injection.
    
    This class accepts all dependencies through its constructor, making it
    easy to test and configure different components independently.
    """
    
    def __init__(self, database_config: DatabaseConfig) -> None:
        """Initialize the application with dependencies.
        
        Args:
            database_config: Database configuration for repository creation
        """
        self.database_config = database_config
        self._repo_factory = CheckpointRepoFactory()
        
    async def initialize(self) -> None:
        """Initialize application components.
        
        This method sets up the repository and other components that require
        async initialization.
        
        Raises:
            RuntimeError: If initialization fails
        """
        try:
            # Create repository using injected configuration
            self.checkpoint_repo = self._repo_factory.create_checkpoint_repo(
                self.database_config
            )
            logger.info(
                f"Initialized {self.database_config.database_type} checkpoint repository"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise RuntimeError(f"Application initialization failed: {e}") from e
    
    async def run(self) -> None:
        """Run the main application logic.
        
        This is where the core email processing logic would go.
        Currently demonstrates repository usage.
        """
        logger.info("Starting email processing...")
        
        # Example: Use the repository
        async with self.checkpoint_repo as repo:
            # TODO: Implement actual email processing logic
            logger.info("Repository is ready for email processing")
            
        logger.info("Email processing completed")
    
    async def shutdown(self) -> None:
        """Clean shutdown of application components."""
        logger.info("Shutting down application...")
        # Any cleanup logic would go here


def create_app(settings: Settings) -> MailTrashSorterApp:
    """Create application with dependency injection.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured application instance
    """
    return MailTrashSorterApp(database_config=settings.database)


def setup_logging(verbose: bool) -> None:
    """Setup application logging.
    
    Args:
        verbose: Enable verbose logging
    """
    if verbose:
        logger.info("Verbose logging enabled")


def load_configuration(config_path: str | None) -> Settings:
    """Load application configuration.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Loaded settings
    """
    if config_path:
        logger.info(f"Using configuration from: {config_path}")
    
    return get_settings()


async def run_app(app: MailTrashSorterApp) -> None:
    """Run the application.
    
    Args:
        app: Application instance to run
    """
    try:
        await app.initialize()
        await app.run()
    finally:
        await app.shutdown()


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--config-path", type=click.Path(exists=True), help="Path to configuration file")
def main(verbose: bool, config_path: str | None) -> None:
    """Main entry point for the mail trash sorter application."""
    import asyncio
    
    logger.info("Starting Mail Trash Sorter v0.1.0")
    
    setup_logging(verbose)
    settings = load_configuration(config_path)
    app = create_app(settings)
    
    asyncio.run(run_app(app))


if __name__ == "__main__":
    main()
