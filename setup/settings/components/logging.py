import os
from typing import Any

from setup.settings.components.base_dir_path import BASE_DIR

LOG_DIR = BASE_DIR / 'logs'
PROJECT_LOG_HANDLERS = ['console']

try:
    LOG_DIR.mkdir(exist_ok=True)
except OSError:
    pass
else:
    PROJECT_LOG_HANDLERS.append('app_file')

LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO').upper()
HANDLERS: dict[str, dict[str, str]] = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'standard',
    },
}

if 'app_file' in PROJECT_LOG_HANDLERS:
    HANDLERS['app_file'] = {
        'class': 'logging.FileHandler',
        'filename': str(LOG_DIR / 'app.log'),
        'mode': 'w',
        'formatter': 'standard',
    }

LOGGING: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': HANDLERS,
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'common': {
            'handlers': PROJECT_LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'customer': {
            'handlers': PROJECT_LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'audit': {
            'handlers': PROJECT_LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'setup': {
            'handlers': PROJECT_LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}
