from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('host_history.views',
       url(r'^$', 'list_logs', name='list_logs'),
       url(r'^list/(all)?$', 'list_logs', name='list_logs'),
   )

# vim:set et sts=4 ts=4 tw=80:
