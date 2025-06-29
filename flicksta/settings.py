import os
from pathlib import Path
from urllib.parse import urlparse
import dj_database_url
from environ import Env

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

# Initialize environment variables
env = Env()

# Set the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from .env
env.read_env(BASE_DIR / '.env')

# Environment configuration
ENVIRONMENT = env('ENVIRONMENT', default='production')

SECRET_KEY = env('SECRET_KEY')

# Debug configuration
IS_DEBUG = env.bool('IS_DEBUG', default=False)
print("IS_DEBUG:", IS_DEBUG)

if ENVIRONMENT == 'development' or IS_DEBUG:
    DEBUG = True
else:
    DEBUG = False
    
# ==============================================================================
# HOST CONFIGURATION
# ==============================================================================

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = (
    '127.0.0.1',
    'localhost',
)

# ==============================================================================
# FEATURE FLAG CONFIGURATION
# ==============================================================================

STAGING = env.bool('STAGING', default=False)
DEVELOPER = env('DEVELOPER', default='')

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    'django.contrib.sites',
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage", # Cloudinary storage for media files
    "django.contrib.staticfiles",
    
    # Third-party apps
    "cloudinary",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_cleanup.apps.CleanupConfig',
    "django_htmx",
    
    # Local apps
    "f_posts",
    "f_users",
    "f_features",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "flicksta.urls"

# ==============================================================================
# TEMPLATE CONFIGURATION
# ==============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "flicksta.wsgi.application"

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if ENVIRONMENT == 'production':
    # DATABASES["default"] = dj_database_url.parse(env('DATABASE_URL'))
    url = urlparse(env('DATABASE_URL'))
    print(f"Using DATABASE_URL: {env('DATABASE_URL')}")
    print(f"Parsed DATABASE_URL: {url}")    
    DATABASES["default"] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': url.path[1:],  # Remove leading slash
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': url.port,
        'OPTIONS': {
            'sslmode': 'require',  # Add only if you need SSL
        },
    }

# ==============================================================================
# AUTHENTICATION CONFIGURATION
# ==============================================================================

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Django Allauth settings
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/profile/onboarding/'
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_USERNAME_BLACKLIST = ['admin', 'static', 'accounts', 'profile', 'category', 'post', 'inbox', 'theboss']

# Email configuration
if ENVIRONMENT == 'production':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = env('EMAIL_ADDRESS')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'Flicksta <' + env('EMAIL_ADDRESS') + '>'
    print("Using SMTP email backend for production")
    ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Flicksta]'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC FILES CONFIGURATION
# ==============================================================================

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ==============================================================================
# MEDIA FILES CONFIGURATION
# ==============================================================================

MEDIA_URL = '/media/'

# Cloudinary configuration for production, local filesystem for development
if ENVIRONMENT == 'production':
    CLOUDINARY_URL = env("CLOUDINARY_URL")
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    print("Using Cloudinary for media storage")
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = BASE_DIR / "media"
    print("Using local filesystem for media storage")

# ==============================================================================
# DEFAULT FIELD CONFIGURATION
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==============================================================================
# DEBUG INFORMATION
# ==============================================================================

# Debug information
print(f"Current environment: {ENVIRONMENT}")
print(f"DEBUG mode: {DEBUG}")
print(f"DEFAULT_FILE_STORAGE: {DEFAULT_FILE_STORAGE}")