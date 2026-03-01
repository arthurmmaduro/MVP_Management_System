import os
from typing import Any

from setup.settings.components.base_dir_path import BASE_DIR

LOG_DIR = BASE_DIR / 'logs'
LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO').upper()

LOGGING: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '%(levelname)s %(asctime)s %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'standard'},
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'common': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
        'customer': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
        'setup': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
    },
}

try:
    LOG_DIR.mkdir(exist_ok=True)
except OSError:
    pass
else:
    LOGGING['handlers']['app_file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': str(LOG_DIR / 'app.log'),
        'maxBytes': 5 * 1024 * 1024,
        'backupCount': 3,
        'formatter': 'standard',
    }
    for logger_name in ('common', 'customer', 'setup'):
        LOGGING['loggers'][logger_name]['handlers'].append('app_file')
