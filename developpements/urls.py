from django.conf.urls.defaults import *

urlpatterns = patterns('developpements.views',
    (r'^$', 'home'),
    (r'^liste/$', 'liste'),
    (r'^versions/$', 'versions'),
    (r'^change_color/$', 'change_color'),
    (r'^done/$', 'done'),
    (r'^modify/$', 'modify'),
)
