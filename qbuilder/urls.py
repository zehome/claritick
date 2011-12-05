from django.conf.urls.defaults import *

urlpatterns = patterns('qbuilder.views',
    url(r'^$', 'home', name="qbuilder_home"),
    url(r'^(?P<query_ids>[\d,]+)/$', 'views_highcharts', name="qbuilder_home"),
    url(r'^edit/(?P<query_id>\d+)/$', 'edit', name="qbuilder_edit"),
    (r'^create/$', 'create'),
    (r'^vue_test', 'vue_test'),
)
