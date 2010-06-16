# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('ticket.views',
    url(r'^partial_new/$', 'partial_new', name="ticket_partial_new"),
    url(r'^new/$', 'new', name="ticket_new"),
    url(r'^modify/(?P<ticket_id>\d+)/$', 'modify', name="ticket_modify"),
    url(r'^view/$', 'list_view', name="ticket_list_view"),
    url(r'^view/(?P<view_id>\d+)/$', 'list_view', name="ticket_list_view"),
    url(r'^list/$', 'list_all', name="ticket_list"),
    url(r'^list/all/$', 'list_all', name="ticket_list_all"),
    url(r'^list/me/$', 'list_me', name="ticket_list_me"),
    url(r'^list/unassigned/$', 'list_unassigned', name="ticket_list_unassigned"),
    url(r'^list/nonvalide/$', 'list_nonvalide', name="ticket_list_nonvalide"),
    url(r'^getfile/(?P<file_id>\d+)/$', 'get_file', name="ticket_get_file"),
    ## Ajax
    url(r'^ajax_load_child/(?P<ticket_id>\d+)/$', 'ajax_load_child', name='ajax_load_child'),
    url(r'^ajax_load_telephone/', 'ajax_load_telephone', name='ajax_load_telephone'),
    url(r'^ajax_graph_permonth/', 'ajax_graph_permonth', name='ajax_graph_permonth'),
    url(r'^ajax_graph_average_close_time/', 'ajax_graph_average_close_time', name='ajax_graph_average_close_time'),

)
