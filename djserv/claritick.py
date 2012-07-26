import os.path
import sys
import logging
basepath = os.path.abspath(os.path.dirname(__file__))

###########################################################################
# Configuration
#
# Django settings
DJANGO_SETTINGS = 'settings'
DJANGO_SERVE_ADMIN = True # Serve admin files

# Server settings
IP_ADDRESS = '0.0.0.0'
PORT = 3000
SERVER_NAME = 'claritick'
SERVER_THREADS = 8
# Change it to True if you want it to run as daemon, if you use a
# daemon.sh file you should also change it to True
RUN_AS_DAEMON = False
DAEMON_RUN_DIR = '/' # The daemon will change directory to this one
                     # this is needed to prevent unmounting your
                     # disk.

# Launch as root to dynamically chown
SERVER_USER = 'claritick'
SERVER_GROUP = 'ed'

# Log settings
LOGFILE = os.path.join(os.path.expanduser("~%s" % (SERVER_USER,)), 'logs', 'server.log')
LOGLEVEL = 'DEBUG' # if DEBUG is True, overwritten to DEBUG
DEBUG = False

LOG_REQUESTS = True
LOG_REQUESTS_FILENAME = os.path.join(os.path.expanduser("~%s" % (SERVER_USER,)), 'logs', 'access.log')
LOG_REQUESTS_KEEP_DAYS = 60

# It must match with the path given in your daemon.sh file if you are
# using a daemon.sh file to control the server.
PIDFILE = os.path.join(os.path.sep, 'var', 'run', 'djserv.%s.pid' % (SERVER_NAME,))

# Enable SSL, if enabled, the certificate and private key must
# be provided.
SSL = False
SSL_CERTIFICATE = '/full/path/to/certificate'
SSL_PRIVATE_KEY = '/full/path/to/private_key'

# How much time (seconds) a request can long
REQUEST_TIMEOUT = 60
# How much time (seconds) to wait for request to complete 
# before FORCED shutdown
SHUTDOWN_TIMEOUT = 0.5

# You can use this code "as it".
def get_dispatcher(options):
    """
    
    May return a WSGIPathInfoDispatcher, or CherryPyWSGIServer dispatcher (dict)
    """
    options.init()
    # Do NOT import this outside this function !
    from django.core.handlers.wsgi import WSGIHandler
    from wsgiserver import WSGIPathInfoDispatcher
    import django
    from django.conf import settings
    # Logging middleware
    from translogger import TransLogger
    # Custom static media serving
    from mediahandler import MediaHandler
    # HA-Proxy health check handler (only returns 200 OK)
    from healthcheckhandler import HealthCheckHandler
    
    app = WSGIHandler()
    mediaHandler = MediaHandler([ settings.STATIC_ROOT, ])
    staticHandler = MediaHandler([ settings.STATIC_ROOT, ])
    healthcheckHandler = HealthCheckHandler()

    if options.LOG_REQUESTS:
        logAccess = logging.getLogger("wsgi.core")
        app = TransLogger(app, setup_console_handler = False,
                          logger = logAccess, logging_level=logging.DEBUG)
        mediaHandler = TransLogger(mediaHandler, setup_console_handler = False,
                                   logger = logAccess, logging_level=logging.DEBUG)
        staticHandler = TransLogger(staticHandler, setup_console_handler = False,
                                   logger = logAccess, logging_level=logging.DEBUG)
        # setup logging
        log_filename = getattr(options, "LOG_REQUESTS_FILENAME", "access.log")
        log_days     = getattr(options, "LOG_REQUESTS_KEEP_DAYS", 60) # 60 days default
        new_handler  = logging.handlers.TimedRotatingFileHandler(log_filename, when = "D", interval = 1, backupCount = log_days)
        
        logAll = logging.getLogger("wsgi")               
        logAll.addHandler(new_handler)
        logAll.setLevel(logging.DEBUG)

    dispatcher = WSGIPathInfoDispatcher( 
        {   '/health': healthcheckHandler,
            '/': app,
			settings.STATIC_URL: staticHandler,
			settings.MEDIA_URL: mediaHandler,
        }
    )
    return dispatcher

# Hack to permit initializing python interpreter inside the djserv cluster
def init():
    """ Initialize python interpreter """
    sys.path.insert(0, '/home/ed')
    sys.path.insert(0, '/home/claritick')
    sys.path.insert(0, '/home/claritick/claritick')

def get_external_processes(options):
    from djserv import ExternalCommandDaemon
    return [ 
        {"class": ExternalCommandDaemon, 
         "kwargs": {"command": "send_emails", "options": options, "interval": 60}
        },
    ]
#
###########################################################################
