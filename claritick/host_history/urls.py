from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('host_history.views',
       url(r'^$', 'list_logs', name='list_logs'),
       url(r'^list/$', 'list_logs', name='list_logs'),
       url(r'^list/(host)/(\S*)$', 'list_logs', name='list_logs'),
       url(r'^list/(user)/(\S*)$', 'list_logs', name='list_logs'),
       url(r'^show_diff/(\d+)','view_changes',name='view_changes'),
   )

# vim:set et sts=4 ts=4 tw=80:
