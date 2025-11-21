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
    logger.setLevel(logging.INFO)

    # Prevent re-initialization and duplicate handlers
    if not logger.handlers:
        # Create a StreamHandler to output logs to console (stdout)
        handler = logging.StreamHandler(sys.stdout)

        # Define the log format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # 🔧 Prevent this logger from propagating messages to the root logger
    logger.propagate = False

    return logger
