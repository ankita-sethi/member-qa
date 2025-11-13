from pathlib import Path
import os      # ADD THIS

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-_p=k$=j%+#o=#@wg#+^9l!ik7i14&*vwq%*h@oz+t_zktesh=h'

# IMPORTANT FOR RENDER
DEBUG = False   # CHANGE THIS → Render needs production mode

# ALLOWED HOSTS
ALLOWED_HOSTS = ["*"]   # ADD THIS (Render replaces with its own hostname)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # ADD THIS ↓↓↓ (MUST be directly after SecurityMiddleware)
    "whitenoise.middleware.WhiteNoiseMiddleware",

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qa_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'qa_service.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# STATIC FILES FOR RENDER -----------------------------------------
STATIC_URL = "/static/"        # keep
STATIC_ROOT = BASE_DIR / "staticfiles"     # ADD THIS
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"  # ADD THIS


# When behind Render’s proxy ensure HTTPS works correctly
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")   # ADD THIS

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
