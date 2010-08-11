from django.conf.urls.defaults import *

urlpatterns = patterns('developpements.views',
    (r'^$', 'home'),
    (r'^liste/(?P<project_id>\d+)/$', 'liste'),
    (r'^dev_dialog/(?P<dev_pk>\d+)/$', 'dev_dialog'),
    (r'^shortlist/(?P<project_id>\d+)/$', 'shortlist'),
    (r'^versions/(?P<project_id>\d+)/$', 'versions'),
    (r'^change_color/$', 'change_color'),
    (r'^save_item_field/$', 'save_item_field'),
    (r'^done/$', 'done'),
    (r'^bug/$', 'bug'),
    (r'^modify/$', 'modify'),
    (r'^populate_field/$', 'populate_field'),
)
