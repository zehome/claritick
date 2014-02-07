from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from api import public_views


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
