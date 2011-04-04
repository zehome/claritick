# -*- coding=utf8 -*-
# Create your views here.
from host_history.models import HostEditLog, Host, HostVersion
from host_history.forms import SearchLogForm
from common.diggpaginator import DiggPaginator
from django.http import Http404

from django.conf import settings
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import permission_required

@permission_required("host_history.can_access_host_history")
def list_logs(request, filter_type=None, filter_key=None):
    """
    Cette fonction gère le tri et l'affichage de l'historique des hotes
    Elle sert à garder une tracabilité des modifications et états.
    Variables de session:
        - lastpage_log_list: dernière page accédée
        - search_log_list: recherche courrante
        - sort_log_list: garde l'ordre courrent
    """
    sort_default='-date'
    columns = ["host","user","date","ip","action","message","version"]
    new_search = False

    # Url filtering
    if filter_type:
        if filter_type == 'host' and filter_key == 'deleted':
            qs = HostEditLog.objects.filter(host__exact=None)
        elif filter_type == 'user' and filter_key == 'deleted':
            qs = HostEditLog.objects.filter(user__exact=None)
        elif filter_type == 'host':
            qs = get_object_or_404(Host, pk=filter_key).hosteditlog_set
        elif filter_type == 'user':
            qs = get_object_or_404(User, pk=filter_key).hosteditlog_set
        else:
            raise Http404
    else:
        qs = HostEditLog.objects.all()
    qs = qs.select_related('host','user','hostrevision')

    # Reset button
    if request.POST.get("filter_reset",False):
        form = SearchLogForm(request.user,{})
        del(request.session["lastpage_log_list"])
        del(request.session["search_log_list"])
        del(request.session["sort_log_list"])

    # Handle SearchForm filtering
    form = SearchLogForm(request.user, request.POST or
                                     request.session.get("search_log_list",{}))
    if form.is_valid():
        request.session["search_log_list"] = form.cleaned_data
        qs = form.search(qs)

    # Update sorting
    sorting = sort_default
    sort_get = request.GET.get('sort',
                   request.session.get("sort_log_list", sort_default))
    if sort_get in columns:
        sorting = sort_get
    if sort_get.startswith('-') and sort_get[1:] in columns:
        sorting = sort_get
    request.session["sort_log_list"] = sorting

    # Set paginator
    paginator = DiggPaginator(qs.order_by(sorting),
                              settings.HOSTS_PER_PAGE, body=5, tail=2, padding=2)

    # Get page
    page_num = 1
    page_asked = int(request.GET.get('page',
                                     request.session.get('lastpage_log_list', 1)))
    if ((page_asked <= paginator.num_pages) and not new_search):
        page_num = page_asked
    request.session["lastpage_log_list"] = page_num
    page = paginator.page(page_num)
    return render_to_response(
        'host_history/list.html',
        {"page": page,
         "columns": columns,
         "sorting": sorting,
         "form": form},
        context_instance=RequestContext(request))

@permission_required("host_history.can_access_host_history")
def view_changes(request, rev_id):
    version = get_object_or_404(HostVersion, pk = rev_id)
    log = version.log_entry
    print log.message
    message_infos = log.parse_message()
    # Removing last item because it's an empty line.
    host_changes = version.host.split('\n')[:-1]
    fields_changes = version.additionnal_fields.split('\n')[:-1]
    return render_to_response('host_history/view.html',
        {   "host_changes": host_changes,
            "fields_changes": fields_changes,
            "old_hostname": message_infos.group(1),
            "date": log.date,
            "user": log.username,
            "action": message_infos.group(2),
            "log":log,
        },context_instance=RequestContext(request))
