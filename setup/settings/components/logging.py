import os
from typing import Any

from setup.settings.components.base_dir_path import BASE_DIR

LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO').upper()
LOG_HANDLERS = ['console', 'app_file']

LOGGING: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'app_file': {
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'app.log'),
            'mode': 'w',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': LOG_HANDLERS,
        'level': LOG_LEVEL,
    },
    'loggers': {
        'common': {
            'handlers': LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'customer': {
            'handlers': LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'audit': {
            'handlers': LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'setup': {
            'handlers': LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}
