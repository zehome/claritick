from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

import reporting

@login_required
@permission_required("ticket.can_view_report")
def report_list(request):
    reports = reporting.all_reports()
    return render_to_response('reporting/list.html', {'reports': reports}, 
                              context_instance=RequestContext(request))

@login_required
@permission_required("ticket.can_view_report")
def view_report(request, slug):
    report = reporting.get_report(slug)(request)
    data = {'report': report, 'title':report.verbose_name}
    return render_to_response('reporting/view.html', data, 
                              context_instance=RequestContext(request))
