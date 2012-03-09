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
    url(r'^list/notseen/$', 'list_notseen', name="ticket_list_notseen"),
    url(r'^getfile/(?P<file_id>\d+)/$', 'get_file', name="ticket_get_file"),
    ## Ajax
    url(r'^ajax_load_child/(?P<ticket_id>\d+)/$', 'ajax_load_child', name='ajax_load_child'),
    url(r'^ajax_delete_tma/(?P<ticket_id>\d+)/$', 'ajax_delete_tma', name='ajax_delete_tma'),
    url(r'^ajax_load_ticketmailtrace/(?P<ticket_id>\d+)/$', 'ajax_load_ticketmailtrace', name='ajax_load_ticketmailtrace'),
    url(r'^ajax_set_alarm/(?P<ticket_id>\d+)/$', 'ajax_set_alarm', name='ajax_set_alarm'),
    url(r'^ajax_load_telephone/', 'ajax_load_telephone', name='ajax_load_telephone'),
    url(r'^ajax_graph_opentickets/', 'ajax_graph_opentickets', name='ajax_graph_opentickets'),
    url(r'^ajax_graph_closetickets/', 'ajax_graph_closetickets', name='ajax_graph_closetickets'),
    url(r'^ajax_graph_recall/', 'ajax_graph_recall', name='ajax_graph_recall'),
    url(r'^ajax_graph_average_close_time/', 'ajax_graph_average_close_time', name='ajax_graph_average_close_time'),

    url(r'^ajax_mark_all_ticket_seen/$', 'ajax_mark_all_ticket_seen', name='ajax_mark_all_ticket_seen'),
    url(r'^ajax_reset_all_ticket_seen/$', 'ajax_reset_all_ticket_seen', name='ajax_reset_all_ticket_seen'),

    ## Chrome extension / feeds
    url(r'^feed/', 'ticket_feed', name='ticket_feed'),

    # Stats
    url(r'^stats/', 'ticket_stats', name='ticket_stats'),
)

# Exports
urlpatterns += patterns('ticket.exportviews',
    url(r'^export/all.csv$', 'export_all', name='ticket_export_all'),
    url(r'^export/me.csv$', 'export_me', name='ticket_export_me'),
    url(r'^export/notseen.csv$', 'export_notseen', name='ticket_export_notseen'),
    url(r'^export/unassigned.csv$', 'export_unassigned', name='ticket_export_unassigned'),
    url(r'^export/nonvalide.csv$', 'export_nonvalide', name='ticket_export_nonvalide'),
    )
