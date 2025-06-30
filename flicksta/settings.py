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
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
else:
    DEBUG = False
    
# ==============================================================================
# HOST CONFIGURATION
# ==============================================================================
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', default=None)
if RENDER_EXTERNAL_HOSTNAME is not None:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

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
# FILE UPLOAD SECURITY CONFIGURATION
# ==============================================================================

# Maximum file size (in bytes) - 10MB default
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int('FILE_UPLOAD_MAX_MEMORY_SIZE', default=10 * 1024 * 1024)  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int('DATA_UPLOAD_MAX_MEMORY_SIZE', default=10 * 1024 * 1024)  # 10MB

# Maximum total upload size
DATA_UPLOAD_MAX_NUMBER_FIELDS = env.int('DATA_UPLOAD_MAX_NUMBER_FIELDS', default=1000)

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']

# File type specific size limits (in bytes)
MAX_IMAGE_SIZE = env.int('MAX_IMAGE_SIZE', default=5 * 1024 * 1024)  # 5MB

# Rate limiting settings
UPLOAD_RATE_LIMIT = {
    'per_minute': env.int('UPLOADS_PER_MINUTE', default=10), # Default 10 uploads per minute
    'per_hour': env.int('UPLOADS_PER_HOUR', default=100), # Default 100 uploads per hour
    'per_day': env.int('UPLOADS_PER_DAY', default=200), # Default 500 uploads per day   
}

CREATE_POST_RATE_LIMIT = {
    'per_minute': env.int('POSTS_PER_MINUTE', default=10), # Default 10 posts per minute
    'per_hour': env.int('POSTS_PER_HOUR', default=100), # Default 100 posts per hour
    'per_day': env.int('POSTS_PER_DAY', default=200), # Default 200 posts per day
}

EMAIL_RATE_LIMIT = {
    'per_minute': env.int('EMAILS_PER_MINUTE', default=2), # Default 2 emails per minute
    'per_hour': env.int('EMAILS_PER_HOUR', default=10), # Default 10 emails per hour
    'per_day': env.int('EMAILS_PER_DAY', default=20), # Default 50 emails per day
}

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # "cloudinary_storage", # Cloudinary storage for media files
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    
    # Third-party apps
    # "cloudinary",
    "storages",  # For AWS S3 storage
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_cleanup.apps.CleanupConfig",
    "django_htmx",
    "django_ratelimit",
    
    # Local apps
    "f_posts",
    "f_users",
    "f_features",
    "f_landingpages",
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
    
    # User defined middleware
    "f_landingpages.middleware.landingpage_middleware",
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
# CACHE CONFIGURATION (for rate limiting)
# ==============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),
    } if ENVIRONMENT == 'production' else {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Rate limiting backend
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_ENABLE = True

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

STORAGE_SERVICE = env('STORAGE_SERVICE', default='cloudinary')  # 'aws' or 'cloudinary'
MEDIA_URL = '/media/'

# Cloudinary configuration for production, local filesystem for development
if ENVIRONMENT == 'production':
    if STORAGE_SERVICE == 'cloudinary':
        # FOR CLOUDINARY AS MEDIA STORAGE  
        CLOUDINARY_URL = env("CLOUDINARY_URL")
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
        STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticCloudinaryStorage'
        print("Using Cloudinary for media storage")
    elif STORAGE_SERVICE == 'aws':
        # FOR AWS S3 AS MEDIA STORAGE
        AWS_ACCESS_KEY_ID = env('AWS_S3_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = env('AWS_S3_SECRET_ACCESS_KEY')
        AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
        AWS_S3_SIGNATURE_VERSION = 's3v4'
        AWS_S3_ADDRESSING_STYLE = 'virtual'
        AWS_DEFAULT_ACL = None
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400',
        }
        AWS_S3_FILE_OVERWRITE = False
        AWS_QUERYSTRING_AUTH = True
        # Use custom storage classes
        STORAGES = {
            "default": {
                "BACKEND": "flicksta.storages.MediaStorage",
            },
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        }
        
        # Backward compatibility
        DEFAULT_FILE_STORAGE = 'flicksta.storages.MediaStorage'
        
        print("Using AWS S3 for media storage")
        print(f"AWS_STORAGE_BUCKET_NAME: {AWS_STORAGE_BUCKET_NAME}")
        print(f"AWS_S3_REGION_NAME: {AWS_S3_REGION_NAME}")
    else:
        raise ValueError("Invalid STORAGE_SERVICE specified. Use 'cloudinary' or 'aws'.")
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    MEDIA_ROOT = BASE_DIR / "media"
    print("Using local filesystem for media storage")

# ==============================================================================
# DEFAULT FIELD CONFIGURATION
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==============================================================================
# SECURITY CONFIGURATION
# ==============================================================================

# Content Security Policy
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# File upload security
SECURE_FILE_UPLOAD = True

# ==============================================================================
# DEBUG INFORMATION
# ==============================================================================

# Debug information
print(f"Current environment: {ENVIRONMENT}")
print(f"DEBUG mode: {DEBUG}")
print(f"DEFAULT_FILE_STORAGE: {DEFAULT_FILE_STORAGE}")