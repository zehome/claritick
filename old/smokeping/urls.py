from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('smokeping.views',
    url(r'.*', 'smokeping', name='smokeping'),
)
