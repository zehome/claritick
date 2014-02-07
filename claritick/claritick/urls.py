from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.conf import settings
from api import urls as api_urls


urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(url='/app/index.html'),
        name='go-to-webui'),
    url(r'^api/', include(api_urls)),
)

if settings.DEBUG:
    import mimetypes
    from django.conf.urls.static import static
    mimetypes.add_type("application/font-woff", ".woff", True)
    urlpatterns += static('/app/', document_root=settings.WEBUI_ROOT)
