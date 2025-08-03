"""
Secure logging configuration for MusicSeeker
"""

import logging
import logging.config
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
        'security': {
            'format': '[%(asctime)s] SECURITY %(levelname)s: %(message)s',
        }
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/musicseeker.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'security_file': {
            'formatter': 'security',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['default', 'file'],
        },
        'security': {
            'level': 'INFO',
            'handlers': ['security_file'],
            'propagate': False,
        },
        'openai': {
            'level': 'WARNING',  # Prevent API key leaks
            'handlers': ['file'],
            'propagate': False,
        },
        'sqlalchemy.engine': {
            'level': 'WARNING',  # Prevent SQL query logging in production
            'handlers': ['file'],
            'propagate': False,
        }
    }
}


def setup_logging():
    """Configure secure logging"""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Test security logger
    security_logger = logging.getLogger("security")
    security_logger.info("Security logging initialized")


def safe_log_query(query: str) -> str:
    """Safely log search queries without exposing sensitive info"""
    if len(query) > 50:
        return f"{query[:47]}..."
    return query


def safe_log_error(error: str) -> str:
    """Safely log errors without exposing sensitive paths or API keys"""
    # Remove potential API keys
    import re
    error = re.sub(r'sk-[a-zA-Z0-9-_]{20,}', '[API_KEY_REDACTED]', error)
    
    # Remove full file paths
    error = re.sub(r'/[^\\s]*(/[^\\s]*)+', '[PATH_REDACTED]', error)
    
    return error
