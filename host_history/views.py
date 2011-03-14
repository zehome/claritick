# Create your views here.
from clariadmin.models import HostEditLog
from common.diggpaginator import DiggPaginator
from django.conf import settings

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required

@permission_required("clariadmin.can_access_clariadmin")
def list_logs(request):
    sort_default='-date'
    columns = ["host","user","date","ip","action","message"]
    new_search = False

    # get sorting
    sorting = sort_default
    sort_get = request.GET.get('sort',
                   request.session.get("sort_log_list", sort_default))
    if sort_get in columns:
        sorting = sort_get
    if sort_get.startswith('-') and sort_get[1:] in columns:
        sorting = sort_get
    request.session["sort_log_list"] = sorting

    paginator = DiggPaginator(HostEditLog.objects.all().select_related('host','user'), settings.HOSTS_PER_PAGE, body=5, tail=2, padding=2)

    # get page
    page_num = 1
    page_asked = int(request.GET.get('page',
                                     request.session.get('lastpage_host-history', 1)))
    if ((page_asked <= paginator.num_pages) and not new_search):
        page_num = page_asked
    request.session["lastpage_host-history"] = page_num

    page = paginator.page(page_num)
    return render_to_response(
        'host_history/list.html',
        {"page": page,
         "columns": columns},
        context_instance=RequestContext(request))
