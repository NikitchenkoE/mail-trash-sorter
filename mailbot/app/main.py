"""Main entry point for the mail trash sorter application."""

import click
from loguru import logger


@click.command()
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose logging"
)
@click.option(
    "--config-path",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
def main(verbose: bool, config_path: str | None) -> None:
    """Main entry point for the mail trash sorter application.
    
    Args:
        verbose: Enable verbose logging output
        config_path: Optional path to configuration file
    """
    if verbose:
        logger.info("Verbose logging enabled")
    
    logger.info("Starting Mail Trash Sorter v0.1.0")
    
    if config_path:
        logger.info(f"Using configuration from: {config_path}")
    
    # TODO: Implement main application logic
    logger.info("Mail Trash Sorter is ready to start organizing your emails!")


if __name__ == "__main__":
    main()
