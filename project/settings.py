"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'false'

ALLOWED_HOSTS = [
    'your-app-name.onrender.com',  # Replace with your Render domain
    'localhost',
    '127.0.0.1'
]


# Application definition

INSTALLED_APPS = [
    'daphne',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'dev',
    'customer.apps.CustomerConfig',
    'channels',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'project.middleware.NextParameterMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'project' / 'templates',
            BASE_DIR / 'customer' / 'templates',
            BASE_DIR / 'dev' / 'templates',
            BASE_DIR / 'chat' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add these settings after STATIC_URL configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure the media directories exist
PROFILE_PICS_DIR = os.path.join(MEDIA_ROOT, 'profile_pics')
os.makedirs(PROFILE_PICS_DIR, exist_ok=True)

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Social Auth settings
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/auth-redirect/'
SOCIAL_AUTH_LOGIN_ERROR_URL = 'login'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '842002200695-8so8lasrmnep7go3daosnkemi2eti7ea.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

# Login/Logout URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'choose_role'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'

# Add these constants for group names
DEVELOPER_GROUP = 'Developer'
CUSTOMER_GROUP = 'Customer'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'project.pipeline.assign_user_group',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/auth-redirect/'

# Update social auth settings
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {'prompt': 'select_account'}
SOCIAL_AUTH_STRATEGY = 'social_django.strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social_django.models.DjangoStorage'

# Add these settings for iframe support
X_FRAME_OPTIONS = 'SAMEORIGIN'  # This allows iframes from the same domain
SECURE_REFERRER_POLICY = 'same-origin'
XS_SHARING_ALLOWED_ORIGINS = '*'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']

# If you need to allow specific external domains to be loaded in iframes, use:
CSRF_TRUSTED_ORIGINS = [
    'https://your-app-name.onrender.com',  # Replace with your Render domain
    'https://github.com',
]

# For development, you might want to disable CSP (Content Security Policy)
# Only do this in development, not in production!
if DEBUG:
    MIDDLEWARE = [
        middleware for middleware in MIDDLEWARE
        if middleware != 'django.middleware.security.SecurityMiddleware'
    ]

# ZegoCloud Settings
ZEGO_APP_ID = 1443711733
ZEGO_SERVER_SECRET = 'b1696a248baceb6499b62d3c6189e5fe'

# Channels configuration
ASGI_APPLICATION = 'project.routing.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

# Add these settings if not already present
ASGI_APPLICATION = "project.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Add these for WebSocket security
ALLOWED_HOSTS = ['*']  # In production, replace with your actual domains
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']  # Add your domains
