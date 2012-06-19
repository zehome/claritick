# -*- coding: utf8 -*-

import httplib
import urllib

from django.http import Http404, HttpResponse
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import permission_required

from smokeping.models import Smokeping

def prepreq(d):
    o = []
    for k, v in d.items():
        k = smart_str(k, "ISO-8859-15")
        o.extend([ urllib.urlencode({k: smart_str(v, "ISO-8859-15")}) for v in d.getlist(k)])
    return '&'.join(o)

@permission_required("smokeping.smokeping")
def smokeping(request):
    """
    Proxy to smokeping
    """
    pi = request.path_info
    smokeping_conn = httplib.HTTPConnection("stats.clarisys.fr")

    try:
        client = request.user.get_profile().client
    except:
        return HttpResponse(u"No profile.", status=500)

    smokepings = Smokeping.objects.filter(client=client)
    if not smokepings:
        return HttpResponse(u"Aucun smokeping associe.", status=500)

    # Take first
    smokeping = smokepings[0]

    if pi == "/smokeping/":
        smokeping_conn.request("GET", "%s?%s" % (smokeping.path, prepreq(request.GET)))
    elif pi.startswith("/smokeping/"):
        smokeping_conn.request("GET", str(pi))
    response = smokeping_conn.getresponse()
    if response.status == 200:
        djresponse = HttpResponse(response.read())
        for k,v in response.getheaders():
            djresponse[k] = v
        return djresponse
    else:
        return HttpResponse(u"Erreur", status=500)
