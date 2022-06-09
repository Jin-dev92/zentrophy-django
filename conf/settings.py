"""
Django settings for conf project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import datetime
import os
from pathlib import Path
from conf.contant import Env

ENV = Env.DEVELOPMENT
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-plug1-6zblo)q^z1n2mjdiws96now4r!=l2@&0o$=82dxs3@^2'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV is Env.DEVELOPMENT
# MAIN_URL = ''  # 젠트로피 도메인
# ALLOWED_URL_LIST = ['.pythonanywhere.com', MAIN_URL]
ALLOWED_URL_LIST = ['.pythonanywhere.com']

CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ALLOW_CREDENTIALS = True
# CSRF_TRUSTED_ORIGINS = ['http://*.pythonanywhere.com', 'http://*.127.0.0.1','http://localhost']
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'https://*.pythonanywhere.com', 'http://127.0.0.1:8000']
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [url for url in ALLOWED_URL_LIST]
    CORS_ORIGIN_WHITELIST = ['http://localhost:8080']

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MAX_UPLOAD_SIZE = "10485760"  # 업로드 되는 이미지 파일은 10MB를 넘지 않는다.

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'colorfield',
    'sorl.thumbnail',
    'debug_toolbar',
    # applications
    'post',
    'product',
    'placement',
    'order',
    'history',
    'member',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'conf.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

INTERNAL_IPS = [  # django debug toolbar allow ip list
    '127.0.0.1',
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'  # 로그인 기본값
LOGOUT_URL = '/logout/'  # 로그아웃 기본값
LOGIN_REDIRECT_URL = '/'  # 반드시 정의할 것!
# LOGOUT_REDIRECT_URL = None
AUTH_USER_MODEL = 'member.User'

YEAR_TWO_DIGIT = str(datetime.datetime.now().year)[0:2]
LICENSE_NUMBER_LENGTH = 16
OPTION_SPLIT = "++"
# permmistion groups
ADMIN_GROUP_NAME = 'super_user'
CUSTOMER_GROUP_NAME = None
MAX_DISPLAY_LINE_COUNT = 2
JWT_ENCRYPTION_ALG = 'HS256'
