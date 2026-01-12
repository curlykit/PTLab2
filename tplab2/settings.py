import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =========== БЕЗОПАСНОСТЬ ===========
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-измени-это-на-секретный-ключ-в-продакшене')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['ptlab2-v0xa.onrender.com', 'localhost', '127.0.0.1']

# =========== ПРИЛОЖЕНИЯ ===========
INSTALLED_APPS = [
    'shop.apps.ShopConfig',  # Твоё приложение магазина
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# =========== МИДЛВЭРЫ ===========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для статики на Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tplab2.urls'  # Замени если у тебя другое имя проекта

# =========== ШАБЛОНЫ ===========
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

WSGI_APPLICATION = 'tplab2.wsgi.application'  # Замени если у тебя другое имя проекта

# =========== БАЗА ДАННЫХ ===========
import dj_database_url

# Базовые настройки для локальной разработки
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_db',
        'USER': 'postgres',
        'PASSWORD': 'ps_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Автоматическая настройка для разных сред
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Для продакшена (Render) - используем полную конфигурацию
    if 'render.com' in DATABASE_URL or 'postgres.railway' in DATABASE_URL:
        DATABASES['default'] = dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True  # SSL только для продакшена
        )
    else:
        # Для GitHub Actions и других сред - БЕЗ SSL
        DATABASES['default'] = dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=False  # Без SSL для CI
        )

# ПРОДАКШЕН на Render.com (автоматически переопределит настройки)
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True  # Важно для Render
    )

# =========== ВАЛИДАЦИЯ ПАРОЛЕЙ ===========
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

# =========== ИНТЕРНАЦИОНАЛИЗАЦИЯ ===========
LANGUAGE_CODE = 'ru-ru'  # Или 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =========== СТАТИЧЕСКИЕ ФАЙЛЫ ===========
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Для collectstatic
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========== ДЛЯ ТЕСТОВ ===========
TEST_RUNNER = 'test_runner.ColorfulTestRunner'

# =========== ДЕБАГ ИНФОРМАЦИЯ (можно убрать в продакшене) ===========
if DEBUG:
    print("=== DATABASE CONFIGURATION ===")
    print(f"DATABASE_URL from env: {os.environ.get('DATABASE_URL')}")
    print(f"DATABASES default config: {DATABASES['default']}")
    
    # Проверка подключения к базе
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ DATABASE: Connection successful")
    except Exception as e:
        print(f"❌ DATABASE: Connection failed - {e}")