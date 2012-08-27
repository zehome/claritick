# -*- coding: utf-8 -*-

import traceback

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import HttpResponse

from etiquette_printer.forms import PrintOrderForm, PermissionDenied
from etiquette_printer import tasks


@permission_required('etiquette_printer.print_etiquettetemplate')
def get_dialog(request):
    return render(request, "etiquette_printer/test.html", {})


@permission_required('etiquette_printer.print_etiquettetemplate')
def ajax_print_etiquette(request):
    if request.POST and 'template' in request.POST:
        form = PrintOrderForm(request.POST, app_name=request.GET.get("app"), model_name=request.GET.get("model"))
        if form.is_valid():
            error = False
            errorMessage = u"Erreur inconnue."
            try:
                output_data = form.get_output(int(request.POST.get('obj_pk')), request.user)
            except PermissionDenied:
                error = True
                errorMessage = "Permission insuffisantes."
            except:
                error = True
                errorMessage = "Formattage impossible:\n%s" % (traceback.format_exc(),)

            if not error:
                try:
                    error = not tasks.send_to_printer(output_data, form.cleaned_data["template"].printer_ip)
                except:
                    error = True
                    errorMessage = "Impression impossible:\n%s" % (traceback.format_exc(),)

            if error:
                return HttpResponse(
                    "<span style=\"color: red\">Print command failed:"
                    "</span><p>%s</p>" % (errorMessage,)
                )
            else:
                return HttpResponse("<span style=\"color: green\">Impression terminée.</span>") 
    else:
        form = PrintOrderForm(app_name=request.GET.get("app"), model_name=request.GET.get("model"))
    return render(request, "etiquette_printer/ajax_dialog.html", {
        'form': form,
    })
