DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS: list[str] = []

LOCAL_APPS: list[str] = [
    'audit.apps.AuditConfig',
    'home.apps.HomeConfig',
    'customer.apps.CustomerConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
