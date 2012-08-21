# -*- coding: utf-8 -*-

import os
basepath = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Laurent Coustet', 'ed@zehome.com'),
)

MANAGERS = ADMINS
DATABASES = {
    "default": {
        # to use unaccentued search, install:
        #    https://launchpad.net/postgresql-unaccent
        # and use:
        # "ENGINE": 'common.unaccent_postgres_psycopg2',

        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "NAME": 'claritick',
        "USER": 'claritick',
        "PASSWORD": '',
        "HOST": "localhost",
        "PORT": "5432"
    }
}

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

MEDIA_ROOT = os.path.join(basepath, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(basepath, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(basepath, 'media'),
    ("qbuilder", os.path.join(basepath, 'qbuilder', 'media')),
    ("dojango", os.path.join(basepath, 'dojango', 'dojo-media')),
)


# Make this unique, and don't share it with anybody.
SECRET_KEY = '9hart)zyl_0=u7$xj@+!d@6(^8&nmvni5r@898ko!rrp5spj-e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
#        ),
#    ),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dojango.middleware.DojoCollector',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'common.middleware.userprofile.LazyProfileToUserMiddleware',
    'common.exceptionmiddleware.UserBasedExceptionMiddleware',
    'backlinks.middleware.BacklinksMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'ticket.middleware.PopulateUserMiddleware',
    #'django.middleware.gzip.GZipMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'common.middleware.profiling.ProfileMiddleware',
    'common.middleware.autologout.AutoLogout',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media", # Legacy support
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "dojango.context_processors.config",
    'django.core.context_processors.csrf',
    'django.core.context_processors.request',
    'ticket.context_processors.ticket_views',
    'lock.context_processors.lock_settings',
    'profiletools.context_processors.fetch_profile',
)


ROOT_URLCONF = 'claritick.urls'

TEMPLATE_DIRS = (
    os.path.join(basepath, 'templates'),
    os.path.join(basepath, 'qbuilder', 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sites',    # Needed for comment
    'django.contrib.contenttypes',
    'django.contrib.staticfiles', # Media static from django
    'django.contrib.sessions',
    'django.contrib.admin',    # Site admin
    'django.contrib.comments', # Commentaires
    'dojango',                 # Dojo/Django Dojango
    'common',
    'ticket',
    'ticket_comments',
    'clariadmin',              # Clariadmin
    'host_history',            # Clariadmin hosts versioning
    'qsstats',                 # Fun with aggregates ;)
    'backlinks',               # Return to page saved in sessions
    'chuser',                  # Switch user
    'lock',                    # Lock objects by users
    'packaging',               # Clarideploy tools
    'debug_toolbar',
    'desktopnotifications',
    'bondecommande',
    'etiquette_printer',       # Impression d'étiquettes codebarre
    'qbuilder',
    'loggingauth',             # Logs login/logout
    'smokeping',               # Logs login/logout
    'rappel',                  # Create ticket rappel
    'django_extensions',
)

COMMENTS_APP = 'ticket_comments'

AUTH_PROFILE_MODULE = 'common.UserProfile'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Paramètres application "comment"
COMMENTS_HIDE_REMOVED=True
SITE_ID=1

# Formats de date
DATE_FORMAT = "d/m/Y"
DATETIME_FORMAT = "d/m/Y H\hi"
TIME_FORMAT = "H\hi"

# Dojango config
DOJANGO_DOJO_BUILD_VERSION = "1.6.1"
DOJANGO_DOJO_PROFILE = "local_release"
DOJANGO_DOJO_VERSION = "custom_build_161"
DOJANGO_DOJO_THEME = "tundra"
DOJO_BUILD_JAVA_EXEC = "/usr/bin/java"
DOJANGO_BASE_MEDIA_ROOT = os.path.join(basepath, 'dojango', 'dojo-media')
DOJANGO_BASE_MEDIA_URL = "/static/dojango"
DOJANGO_BUILD_MEDIA_URL = "/static/dojango/release"

# Contrôle des emails
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/claritick_emails'
#EMAIL_HOST = "192.168.3.7"

# Authentification backend
AUTHENTICATION_BACKENDS = ('loggingauth.authbackend.LoggingAuthBackend',)

DIALOG_DIALOG = '/usr/bin/dialog'
DIALOG_WIDTH=80
DIALOG_HEIGHT=25

TICKETS_PER_PAGE=50
TICKET_EMAIL_DELAY=120 # delay for 120s before sending email. (Permits grouping)
TICKET_STATE_CLOSED = 4 # pk de l'etat fermé
TICKET_STATE_NEW = 1 # pk de l'etat nouveau
TICKET_STATE_ACTIVE = 2 # pk de l'état actif
TICKET_PRIORITY_NORMAL = 2 # pk de la priorité normale

HOSTS_PER_PAGE = 50
HOST_DEFAULT_ORDER = '-id'

SUMMARY_TICKETS=15 # Nombre de tickets affichés sur la page d'accueil
EMAIL_INTERNAL_COMMENTS = False # Ne transmet pas d'email lorsque l'on poste un commentaire interne
COMMENT_MAX_LENGTH = 65535 * 4

POSTGRESQL_VERSION = 8.4

# Autologout default in minutes
AUTO_LOGOUT_DELAY = 10

# Paramettres de la django-debug-toolbar
# plus d'infos: https://github.com/robhudson/django-debug-toolbar
DEBUG_TOOLBAR_CONFIG={
    'INTERCEPT_REDIRECTS' : False,
}

SVNDOC_CONFIG = {
    'OPENED_BY' : 75,
    'CATEGORY'  : 48,
    'ASSIGNED_TO' : 10,
    'VALIDATOR' : 75,
    'STATE'     : 1,
    'PRIORITY'  : 2,
    'CLIENT'    : 52,
    'SVN_REPOSITORY_TO_CLARITICK_PROJECT' : {
        '/svn/MCA3' : 4,
        '/svn/MCA2' : 4,
        '/svn/ghltest' : 4,
        '/svn/clarilab' : 2,
        }
    }

# Where package files are stored
PACKAGING_ROOT = os.path.join(basepath, 'packaging', 'filestorage')
INTERNAL_IPS = ('127.0.0.1', )
CHROMECRYPTO_KEY = ""

DESKTOP_NOTIFICATION_TAGS = (
    (u"UN", u"Nouvel utilisateur"),
    (u"TA", u"Ticket affecté"),
    (u"TM", u"Ticket modifié"),
    (u"TC", u"Ticket créer"),
    (u"TU", u"Ticket non affecté moidfié"),
    (u"TNR", u"Nouvelle réponse"),
    (u"TCL", u"Ticket fermé"),
)

try:
    from local_settings import *
except ImportError:
    pass

PROFILE_MIDDLEWARE_SORT = ('time', 'calls')
#PROFILE_MIDDLEWARE_STRIP_DIRS=True

# Clariadmin / softupdate key
SOFTUPDATE_KEY="engee4keiShequ1YiuRieyaejohcohjae9naefeisie2eenaeliequahshaShaed"

try:
    from clariadmin.settings import SECURITY
except ImportError:
    print "Unable to load clariadmin settings."
    raise
