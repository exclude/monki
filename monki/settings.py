from pathlib import Path

from django.utils import crypto

from decouple import config, Csv
from dj_database_url import parse as db_url


BASE_DIR = Path(__file__).absolute().parent

ADMINS = (
    ('include', 'contato@xchan.pw'),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default=crypto.get_random_string(32))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool, default=False)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='*')

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd
    'compressor',
    'debug_toolbar',
    'django_cleanup',
    'django_extensions',
    'imagekit',
    'rest_framework',
    # project
    'monki.boards',
    'monki.core',
    'monki.home',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'monki.boards.middleware.UserCookieMiddleware',
    'monki.boards.middleware.UserBanMiddleware',
]

ROOT_URLCONF = 'monki.urls'

# Templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(BASE_DIR / 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'monki.boards.context_processors.inject_categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'monki.wsgi.application'


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'monki.core.middleware.show_toolbar',
    'JQUERY_URL': None,
}

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {'default': config('DATABASE_URL', cast=db_url, default='sqlite:///db.sqlite3')}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

STATICFILES_DIRS = [
    str(BASE_DIR / 'static'),
    str(BASE_DIR.parent / 'node_modules'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR.parent / 'static-root')

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR.parent / 'media-root')

# Django-compressor
# https://django-compressor.readthedocs.org/en/latest/

COMPRESS_PRECOMPILERS = [
    ('text/x-sass', 'django_libsass.SassCompiler'),
    ('text/x-scss', 'django_libsass.SassCompiler'),
]

COMPRESS_ENABLED = not DEBUG

COMPRESS_OFFLINE = True

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]

COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

# Django-libsass
# https://github.com/torchbox/django-libsass

LIBSASS_SOURCEMAPS = True

# Django-imagekit
# https://django-imagekit.readthedocs.io

if not DEBUG:
    IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.Optimistic'

# E-mail
# https://docs.djangoproject.com/en/1.9/topics/email/

DEFAULT_FROM_EMAIL = 'no-reply@xchan.pw'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'no-reply@xchan.pw'
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='123change')
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[XCHAN] '
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Logging
# https://docs.djangoproject.com/en/1.9/topics/logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# File upload
# https://docs.djangoproject.com/en/1.9/topics/http/file-uploads/

FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)


# Django Rest Framework
# http://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'PAGE_SIZE': 10,
}
