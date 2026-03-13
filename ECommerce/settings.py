import os
from pathlib import Path
from dotenv import load_dotenv

# --- 1. BASE CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-patilcraft-key-2026")
# In production we explicitly disable debug and lock down hosts.
DEBUG = False  # ensure this is off on Render

DEFAULT_ALLOWED_HOSTS = [
    'patilcraft.onrender.com',
    'multi-vendor-e-commerce-portal-1.onrender.com',
    'patilapx.tech',
    'www.patilapx.tech',
    'localhost',
    '127.0.0.1',
]

# Merge defaults with optional comma-separated ALLOWED_HOSTS from env.
env_allowed_hosts = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]
ALLOWED_HOSTS = list(dict.fromkeys(DEFAULT_ALLOWED_HOSTS + env_allowed_hosts))

# previous dynamic logic left for reference (commented out)
# ALLOWED_HOSTS = [h for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h]
# if 'RENDER' in os.environ:
#     ALLOWED_HOSTS.append('.onrender.com')
# ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

# --- CSRF Security Configuration ---
DEFAULT_CSRF_TRUSTED_ORIGINS = [
    'https://patilcraft.onrender.com',
    'https://multi-vendor-e-commerce-portal-1.onrender.com',
    'https://patilapx.tech',
    'https://www.patilapx.tech',
]

# Merge defaults with optional comma-separated CSRF_TRUSTED_ORIGINS from env.
env_csrf_origins = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(DEFAULT_CSRF_TRUSTED_ORIGINS + env_csrf_origins))

# keep local dev origins if needed (commented)
# CSRF_TRUSTED_ORIGINS += ['http://localhost:8000', 'http://127.0.0.1:8000']

# --- 2. APPS & MIDDLEWARE ---
INSTALLED_APPS = [
    'jazzmin',  # Must be first for Admin styling - optional admin theme
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites', 
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
    
    # AllAuth & Social Login
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must sit directly after SecurityMiddleware to work correctly
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this for serving static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
]

# --- 3. AUTHENTICATION SETUP ---
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True

# --- 4. SIGNUP & SELLER CONFIGURATION ---
# This matches the class name in your forms.py exactly
ACCOUNT_SIGNUP_FORM_CLASS = 'myapp.forms.SellerSignUpForm'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        "SCOPE": ["profile", "email"],
        'APP': {
            'client_id': os.getenv("GOOGLE_CLIENT_ID"),
            'secret': os.getenv("GOOGLE_SECRET_KEY"),
            'key': ''
        }
    }
}

# --- 5. CORE ENGINE SETTINGS (REWRITTEN FOR MODAL SUPPORT) ---
ROOT_URLCONF = 'ECommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # REQUIRED FOR AUTH MODAL:
                'myapp.context_processors.signup_form_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'ECommerce.wsgi.application'

# --- DATABASE CONFIGURATION ---
# Force PostgreSQL on Render, fallback to SQLite locally
import dj_database_url

if os.environ.get('DATABASE_URL'):
    # Production: Use PostgreSQL provided by Render
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- 6. INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True 

# --- 7. STATIC FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- 8. MEDIA FILES (For uploaded product images, etc) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- 9. JAZZMIN ADMIN STYLING (Modern Dark Theme) ---
JAZZMIN_SETTINGS = {
    "site_title": "Patilcraft Admin",
    "site_header": "Patilcraft Admin Dashboard",
    "site_brand": "Patilcraft",
    "site_logo": "image/logo.png",  
    "login_logo": "image/logo.png",
    "login_logo_below": True,
    "site_logo_classes": "img-circle",
    "welcome_sign": "<span style='font-size: 24px; font-weight: bold; color: #1a2a6c;'> Welcome to Patilcraft Admin</span><br><span style='color: #666; font-size: 14px;'>Manage your e-commerce platform</span>",
    "copyright": "Patilcraft © 2026 | Admin Portal",
    "search_model": "auth.User",
    "user_avatar": None,
    "show_ui_builder": False,
    "navigation": [
        {"app": "auth", "icon": "fas fa-users-cog", "name": "Authentication"},
        {"app": "myapp", "icon": "fas fa-check-circle", "name": "App Management"},
    ],
    "topmenu_links": [
        {"name": "Dashboard",  "url": "admin:index", "permissions": ["auth.view_user"], "icon": "fas fa-home"},
        {"name": "View Website", "url": "/", "new_window": True, "icon": "fas fa-globe"},
        {"name": "Documentation", "url": "https://www.djangoproject.com/", "new_window": True, "icon": "fas fa-book"},
    ],
    "usermenu_links": [
        {"name": "Support", "url": "/", "icon": "fas fa-life-ring"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "custom_css": "css/admin_dashboard.css",
    "custom_js": "js/admin_navbar.js",
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-object-group",
        "myapp.Product": "fas fa-shopping-basket",
        "myapp.CartOrder": "fas fa-cart-arrow-down",
        "myapp.ContactMessage": "fas fa-envelope",
        "myapp.ProductReview": "fas fa-star",
        "myapp.WishlistItem": "fas fa-heart",
        "myapp.Cart": "fas fa-shopping-cart",
        "myapp.CartItem": "fas fa-plus-circle",
        "myapp.Coupon": "fas fa-ticket-alt",
        "myapp.Invoice": "fas fa-file-invoice",
        "myapp.RefundRequest": "fas fa-redo",
        "myapp.NewsletterSubscription": "fas fa-envelope-open",
        "myapp.Profile": "fas fa-user-circle",
        "myapp.SellerAnalytics": "fas fa-chart-bar",
    },
    "order_with_respect_to": ["myapp"],
    "changeform_format": "collapsible",
    "use_google_fonts_cdn": True,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "navbar": "navbar-dark navbar-dark",
    "navbar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "accent": "accent-cyan",
    "brand_colour": "navbar-dark-primary",
    "logo_colour": True,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": True,
    "custom_css": None,
    "custom_js": None,
    "show_fieldsets": True,
    "changeform_format": "collapsible",
    "navigation_expanded": True,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 10. EMAIL (console during development, optional SMTP via env) ---
# For production set EMAIL_HOST in environment variables to enable SMTP
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@patilcraft.local')
if os.getenv('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')
else:
    EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# --- 11. PRODUCTION SECURITY HELPERS (use env vars when deploying) ---
# DEBUG is already False above, so this block will run in production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '3600'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ('1', 'true', 'yes')
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'True').lower() in ('1', 'true', 'yes')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('1', 'true', 'yes')

# --- 12. RAZORPAY PAYMENT GATEWAY CONFIGURATION ---
# Set these in environment variables (.env file or hosting platform)
# Example: RAZORPAY_KEY_ID=rzp_test_xxxxx, RAZORPAY_KEY_SECRET=xxxxxx
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
RAZORPAY_WEBHOOK_ID = os.getenv('RAZORPAY_WEBHOOK_ID', '')

# --- 13. INVOICE SETTINGS ---
CONSOLIDATED_INVOICE = os.getenv('CONSOLIDATED_INVOICE', 'True').lower() in ('1', 'true', 'yes')

# Helpful reminder for production deployments
SECURITY_REMINDERS = {
    'set_debug_false': 'Set DJANGO_DEBUG=False in production',
    'provide_secret': 'Set SECRET_KEY in environment',
    'configure_allowed_hosts': 'Set ALLOWED_HOSTS env var',
}

# simple diagnostic printout when the process starts (appears in Render logs)
if not DEBUG:
    # this will show up in gunicorn/Render logs and help diagnose host/csrf issues
    print(f"[settings] DEBUG={DEBUG} ALLOWED_HOSTS={ALLOWED_HOSTS} CSRF_TRUSTED_ORIGINS={CSRF_TRUSTED_ORIGINS}")
