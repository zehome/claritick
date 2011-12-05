from django.conf.urls.defaults import *

urlpatterns = patterns('qbuilder.views',
    url(r'^$', 'home', name="qbuilder_home"),
    url(r'^(?P<query_ids>[\d,]+)/$', 'views_highcharts', name="qbuilder_home"),
)
