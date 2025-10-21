import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a custom logger instance for a given module/action name.
    This ensures logs are formatted consistently and only attached once to stdout.

    Args:
        name (str): The name of the logger (usually the name of the custom action class).

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)

    # Set the minimum level for this logger (e.g., INFO, DEBUG, WARNING)
    # INFO is usually sufficient for production, DEBUG for development.
    logger.setLevel(logging.INFO)

    # Prevent the logger from being re-initialized and adding duplicate handlers
    if not logger.handlers:
        # Create a StreamHandler to output logs to console (stdout)
        handler = logging.StreamHandler(sys.stdout)

        # Define the log format: [Timestamp] - [LoggerName] - [Level] - [Message]
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # Add the handler
        logger.addHandler(handler)

    return logger
