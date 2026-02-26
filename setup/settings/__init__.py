import os

from split_settings.tools import include, optional

ENV = os.getenv('DJANGO_ENV', 'local')

include(
    'components/path.py',
    'components/base.py',
    'components/apps.py',
    'components/templates.py',
    'components/middleware.py',
    'components/auth.py',
    'components/i18n.py',
    'components/static.py',
    'infrastructure/database.py',
    f'environments/{ENV}.py',
    optional('environments/local_override.py'),
)
