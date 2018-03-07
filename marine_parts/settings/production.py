"""
Django settings for frobshop project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from oscar.defaults import *
from oscar import get_core_apps, OSCAR_MAIN_TEMPLATE_DIR
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), '../apps/', x)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'cs)qm+=(yp=uvrkdam@vteo-giw_(4%4rdqmpq=b0otx9u*1*w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['www.marineparts.us', 'marineparts.us']


# Application definition
FIXTURES_DIRS = (
    'marine_parts.apps.users.fixtures',
)

THIRD_PARTY_APPS = [
    'bootstrap_admin',
    'safedelete',
    'wkhtmltopdf',
    'bootstrap3',
    'django_countries',
    'widget_tweaks',
    'ads',
    'sslserver',
]

SYSTEM_APPS = [
    'marine_parts.apps.users',
    'marine_parts.parts_scrapper',
    'marine_parts.apps.authorize',
    'marine_parts.apps.dashboard.bulk_price_updater'
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
]

INSTALLED_APPS = THIRD_PARTY_APPS + DJANGO_APPS + SYSTEM_APPS \
    + get_core_apps([
        'marine_parts.apps.basket',
        'marine_parts.apps.catalogue',
        'marine_parts.apps.checkout',
        'marine_parts.apps.customer',
        'marine_parts.apps.dashboard',
        'marine_parts.apps.dashboard.catalogue',
        'marine_parts.apps.promotions',
        'marine_parts.apps.search',
        'marine_parts.apps.shipping',
    ])

AUTH_USER_MODEL = 'users.User'

"""
Oscar shop settings
"""
OSCAR_SHOP_NAME = 'Marine Parts'

# Order processing
OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled',),
    'Being processed': ('Processed', 'Cancelled',),
    'Cancelled': (),
}

# Add updater

OSCAR_DASHBOARD_NAVIGATION[1]['children'].append(
    {
        'label': 'Bulk price update',
        'url_name': 'dashboard:bulk-price-updater-index',
    }
)

OSCAR_DASHBOARD_NAVIGATION += [
    {
        'label': 'Shipping',
        'icon': 'icon-truck',
        'children': [
            {
                'label': 'Shipping Methods',
                'url_name': 'dashboard:shipping-method-list'
            }
        ]
    },
]


FILE_UPLOAD_HANDLERS = ("django_excel.ExcelMemoryFileUploadHandler",
                        "django_excel.TemporaryExcelFileUploadHandler")


# Oscar display setting
OSCAR_DEFAULT_CURRENCY = 'USD'
OSCAR_SHOP_TAGLINE = 'Marine parts - Best Shop'

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Allow languages to be selected
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',

    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'marine_parts.urls'

# Disable when there is real email service available
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:8983/solr/marine_parts',
        'ADMIN_URL': 'http://localhost:8983/solr/',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
        'EXCLUDED_INDEXES': ['oscar.apps.search.search_indexes.ProductIndex'],
    },
}
OSCAR_SEARCH_FACETS = {
    'fields': OrderedDict([
    ]),
    'queries': OrderedDict([

    ]),
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # join(BASE_DIR, 'templates'),
            location('templates'),
            OSCAR_MAIN_TEMPLATE_DIR
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                # Oscar templates
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',

                'marine_parts.apps.promotions.context_processors.promotions',
            ],
        },
    },
]

TEMPLATE_DEBUG = ''

BOOTSTRAP_ADMIN_SIDEBAR_MENU = True

WSGI_APPLICATION = 'marine_parts.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'marine_parts_db',
        'USER': 'mp_user',
        'PASSWORD': 'mP19451AxC',
        'HOST': 'marineparts.ca9ar9i4iarq.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# Google Ads
ADS_GOOGLE_ADSENSE_CLIENT = 'ca-pub-xxxxxxxxxxxxxxxx'  # OPTIONAL-DEFAULT TO None

ADS_ZONES = {
    'header': {
        'name': 'Header',
        'ad_size': '800x90',
        'google_adsense_slot': 'xxxxxxxxx',  # OPTIONAL - DEFAULT TO None
        'google_adsense_format': 'auto',  # OPTIONAL - DEFAULT TO None
    },
    'content': {
        'name': 'Content',
        'ad_size': '500x90',
        'google_adsense_slot': 'xxxxxxxxx',  # OPTIONAL - DEFAULT TO None
        'google_adsense_format': 'auto',  # OPTIONAL - DEFAULT TO None
    },
    'sidebar': {
        'name': 'Sidebar',
        'ad_size': '270x270',
        'google_adsense_slot': 'xxxxxxxxx',  # OPTIONAL - DEFAULT TO None
        'google_adsense_format': 'auto',  # OPTIONAL - DEFAULT TO None
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Includes all languages that have >50% coverage in Transifex
# Taken from Django's default setting for LANGUAGES
gettext_noop = lambda s: s
LANGUAGES = (
    ('en-us', gettext_noop('American English')),
    ('es', gettext_noop('Spanish')),
    ('fr', gettext_noop('French')),

)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = location('/home/ubuntu/marine-parts/static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (

)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '../media/')

LOCALE_PATHS = [
    os.path.join('static', 'locale'),
]

OSCAR_MISSING_IMAGE_URL = MEDIA_URL + 'image_not_found.jpg'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'parts@marineparts.com'
EMAIL_HOST_PASSWORD = 'M@rine0470'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SCRAPPER_ROOT = os.path.join(BASE_DIR, 'parts_scrapper/')
