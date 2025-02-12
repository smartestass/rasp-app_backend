"""
Django settings for schedule_creator project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from identity.django import Auth
from dotenv import load_dotenv
import os


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!7oux((ub)$#j%7v==lqx+u0v=i(vz+l8)s1p_i+m&p1t=ma9g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'edu_resources',
    'rest_framework',
    'corsheaders',
    # 'django_auth_adfs',
    # 'allauth',
    # 'allauth.socialaccount',
    # 'ms_identity_web',
    'identity'
]


AUTH_USER_MODEL = 'edu_resources.User'


AUTHENTICATION_BACKENDS = (
    # 'django_auth_adfs.backend.AdfsAuthCodeBackend',
    "django.contrib.auth.backends.ModelBackend",
)

# MSAL ms_identity_web middleware configs
# from ms_identity_web.configuration import AADConfig
# from ms_identity_web import IdentityWebPython
# AAD_CONFIG = AADConfig.parse_json(file_path='aad.config.json')
# MS_IDENTITY_WEB = IdentityWebPython(AAD_CONFIG)
# ERROR_TEMPLATE = 'auth/{}.html' # for rendering 401 or other errors from msal_middleware
# MICROSOFT_CREATE_NEW_DJANGO_USER = True

AUTH = Auth(
    client_id=os.getenv('CLIENT_ID'),
    client_credential=os.getenv('CLIENT_SECRET'),
    redirect_uri=os.getenv('REDIRECT_URI'),
    authority=os.getenv('AUTHORITY'),
    )
#
# AD_URL = os.getenv('AD_URL')
#
# # checkout the documentation for more settings
# AUTH_ADFS = {
#     "AUDIENCE": os.getenv('CLIENT_ID'),
#     "CLIENT_ID": os.getenv('CLIENT_ID'),
#     "CLIENT_SECRET": os.getenv('CLIENT_SECRET'),
#     "SCOPES": ['User.Read',
#                'User.ReadBasic.All',
#                'Group.Read.All',
#                ],
#     'MIRROR_GROUPS': True,
#     "CLAIM_MAPPING": {"first_name": "given_name",
#                       "last_name": "family_name",
#                       "email": "email"},
#     "USERNAME_CLAIM": 'upn',
#     "TENANT_ID": os.getenv('TENANT_ID'),
#     "RELYING_PARTY_ID": os.getenv('CLIENT_ID')
# }
#
# # Configure django to redirect users to the right URL for login
# LOGIN_URL = "django_auth_adfs:login"
# LOGIN_REDIRECT_URL = "/"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
    # 'django_auth_adfs.middleware.LoginRequiredMiddleware',
    # 'ms_identity_web.django.middleware.MsalMiddleware'
]

CORS_ALLOW_ALL_ORIGINS = True  # Или настройте конкретные домены

# MIDDLEWARE.append()

ROOT_URLCONF = 'schedule_creator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     'rasp-app.sfedu.ru'
# ]

WSGI_APPLICATION = 'schedule_creator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'app-rasp',       # Имя базы данных
        'USER': 'postgres',           # Имя пользователя
        'PASSWORD': '54Horror45!',   # Пароль
        'HOST': 'localhost',        # Хост (оставьте localhost)
        'PORT': '5432',             # Порт (по умолчанию 5432)
    }
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

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
