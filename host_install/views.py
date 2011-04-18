from host_install.forms import InstallationOrderForm
from host_install.models import InstallationOrder
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

def modify(request, order_id=None):
    if order_id:
        order = get_object_or_404(InstallationOrder)
    else:
        order=None
    form = InstallationOrderForm(request.POST or None,instance=order)
    if form.is_valid():
        form.save()
    return render_to_response("host_install/order.html",
                              {
                                  "form":form,
                              },
                              context_instance=RequestContext(request)
                             )
