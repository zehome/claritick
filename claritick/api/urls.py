from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from api import public_views
from api import ticket_views


urlpatterns = format_suffix_patterns(patterns(
    '',
    url(
        r'^login$',
        public_views.LoginView.as_view(),
        name='api-login'
    ),
    url(
        r'^logout$',
        public_views.LogoutView.as_view(),
        name='api-logout'
    ),
))

urlpatterns += format_suffix_patterns(patterns(
    '',
    url(
        r'^ticket/state$',
        ticket_views.StateListView.as_view(),
        name='api-ticket-state-list'
    ),
    url(
        r'^ticket/priority$',
        ticket_views.PriorityListView.as_view(),
        name='api-ticket-priority-list'
    ),
    url(
        r'^ticket/list$',
        ticket_views.TicketListView.as_view(),
        name='api-ticket-list'
    ),
))
