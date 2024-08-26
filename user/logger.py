import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

def logger():
    """Logger"""
    # Define the log file name and location
    response_log_file = 'response_errors.log'

    # Create a RotatingFileHandler to log responses other than 2xx and 3xx
    response_handler = RotatingFileHandler(response_log_file, maxBytes=100000, backupCount=10)
    response_handler.setLevel(logging.WARNING)  # Log warning and above messages

    # Create a custom formatter for the response log messages
    response_formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

    # Set the formatter for the response handler
    response_handler.setFormatter(response_formatter)

    # Modify the root logger to include ERROR and above messages
    logging.getLogger().setLevel(logging.ERROR)

    # Create a custom formatter for system error messages
    system_error_formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

    # Get the 'werkzeug' logger
    werkzeug_logger = logging.getLogger('werkzeug')

    # Check if the 'werkzeug' logger has any handlers before setting the formatter
    if werkzeug_logger.handlers:
        werkzeug_logger.handlers[0].setFormatter(system_error_formatter)
    else:
        # If the 'werkzeug' logger has no handlers, add a StreamHandler with the custom formatter
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(system_error_formatter)
        werkzeug_logger.addHandler(stream_handler)


    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            },
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'response_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': response_log_file,
                'maxBytes': 100000,
                'backupCount': 10,
                'formatter': 'default',
                'level': 'WARNING'  # Log warning and above messages
            }
        },
        'root': {
            'level': 'ERROR',
            'handlers': ['wsgi', 'response_handler']  # Add the response_handler to root logger
        }
    })
