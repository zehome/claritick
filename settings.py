# -*- coding: utf-8 -*-

import os
basepath = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Laurent Coustet', 'ed@zehome.com'),
)

MANAGERS = ADMINS

#~ DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#~ DATABASE_NAME = 'claritick.db'             # Or path to database file if using sqlite3.
#~ DATABASE_USER = ''             # Not used with sqlite3.
#~ DATABASE_PASSWORD = ''         # Not used with sqlite3.
#~ DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#~ DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
DATABASE_ENGINE = 'postgresql_psycopg2' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'claritick'    # Or path to database file if using sqlite3.
DATABASE_USER = 'claritick'    # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = 'database.local.zehome.com'  # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5432'         # Set to empty string for default. Not used with sqlite3.

DEFAULT_FROM_EMAIL = 'claritick@clarisys.fr'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

IMAP_SERVER='localhost' # IMAP server used for email2ticket
IMAP_LOGIN=''
IMAP_PASSWORD=''
IMAP_ALLOWED_CONTENT_TYPES = ['application/pdf',]
EMAIL_USER_PK = 79 # User pk who open ticket recevied by email
EMAIL_TICKET_CATEGORY_DEFAULT = 46 # category when open ticket recevied by email

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(basepath, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/adm_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9hart)zyl_0=u7$xj@+!d@6(^8&nmvni5r@898ko!rrp5spj-e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dojango.middleware.DojoCollector',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'common.exceptionmiddleware.UserBasedExceptionMiddleware',
    'backlinks.middleware.BacklinksMiddleware',
    'ticket.middleware.PopulateUserMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "dojango.context_processors.config",
    'django.core.context_processors.csrf',
    'django.core.context_processors.request',
    'ticket.context_processors.ticket_views',
    'chuser.context_processors.chuser',
    'lock.context_processors.lock_settings',
    'developpements.context_processors.projects',
)

ROOT_URLCONF = 'claritick.urls'

TEMPLATE_DIRS = (
    os.path.join(basepath, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sites', # Needed for comment
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'reporting',               # Override admin templates
    'django.contrib.admin',    # Site admin
    'django.contrib.comments', # Commentaires
    'dojango',                 # Dojo/Django Dojango
    'common',
    'ticket',
    'ticket_comments',
    'clariadmin',              # Clariadmin
    'developpements',          # Suivi developpements MCA3
    'importv1',
    'qsstats',                 # Fun with aggregates ;)
    'backlinks',               # Return to page saved in sessions
    'chuser',                  # Switch user
    'lock',                    # Lock objects by users
)

COMMENTS_APP = 'ticket_comments'

AUTH_PROFILE_MODULE = 'common.UserProfile'
LOGIN_REDIRECT_URL = '/'

# Paramètres application "comment"
COMMENTS_HIDE_REMOVED=True
SITE_ID=1

# Formats de date
DATE_FORMAT = "d/m/Y"
DATETIME_FORMAT = "d/m/Y H\hi"
TIME_FORMAT = "H\hi"

# Dojango config
#DOJANGO_DOJO_PROFILE = "google"
DOJANGO_DOJO_PROFILE = "local_release"
DOJANGO_DOJO_VERSION = "1.4.0-dojango-optimized-with-dojo"
#DOJANGO_DOJO_VERSION = "custom_build_141"
DOJO_BUILD_JAVA_EXEC = "/usr/bin/java"
DOJANGO_BASE_MEDIA_ROOT = os.path.join(basepath, 'dojango', 'dojo-media')
DOJANGO_BASE_MEDIA_URL = "/dojango/dojo-media"

# Contrôle des emails
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/claritick_emails'
#EMAIL_HOST = "192.168.3.7"

DIALOG_DIALOG = '/usr/bin/dialog'
DIALOG_WIDTH=80
DIALOG_HEIGHT=25

TICKETS_PER_PAGE=50
TICKET_EMAIL_DELAY=120 # delay for 120s before sending email. (Permits grouping)
TICKET_STATE_CLOSED = 4 # pk de l'etat fermé
TICKET_STATE_NEW = 1 # pk de l'etat nouveau
TICKET_STATE_ACTIVE = 2 # pk de l'état actif
SUMMARY_TICKETS=15 # Nombre de tickets affich�s sur la page d'accueil
EMAIL_INTERNAL_COMMENTS = False # Ne transmet pas d'email lorsque l'on poste un commentaire interne
COMMENT_MAX_LENGTH = 65535 * 4

TICKET_PRIORITY_NORMAL = 2 # pk de la priorité normale
POSTGRESQL_VERSION = 8.3

SVNDOC_CONFIG = {
    'OPENED_BY' : 26,
    'CATEGORY'  : 16,
    'ASSIGNED_TO' : 9,
    'VALIDATOR' : 26,
    'STATE'     : 1,
    'PRIORITY'  : 2,
    'CLIENT'    : 1,
    'SVN_REPOSITORY_TO_CLARITICK_PROJECT' : {
        '/svn/MCA3' : 4,
        '/svn/MCA2' : 4,
        '/svn/clarilab' : 2,
        }
    }
try:
    from local_settings import *
except ImportError:
    pass
