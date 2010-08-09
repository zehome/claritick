from django.conf.urls.defaults import *

urlpatterns = patterns('developpements.views',
    (r'^$', 'home'),
    (r'^liste/(?P<project_id>\d+)/$', 'liste'),
    (r'^versions/(?P<project_id>\d+)/$', 'versions'),
    (r'^change_color/$', 'change_color'),
    (r'^save_item_field/$', 'save_item_field'),
    (r'^done/$', 'done'),
    (r'^bug/$', 'bug'),
    (r'^modify/$', 'modify'),
    (r'^populate_field/$', 'populate_field'),
)
