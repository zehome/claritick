# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest

from common.models import Client, Coordinate
from common.forms import ClientForm, CoordinateForm

import simplejson as json

@login_required
def modify_client(request):
    """
        Vue pour modifier les coordonnées du client courant.
    """
    client = request.user.get_profile().client
    if not client:
        raise Exception(u"Pas de client dans le profil pour l'utilisateur %s." % request.user)
    coordinate = client.coordinates or Coordinate()

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        coordinate_form = CoordinateForm(request.POST, instance=coordinate)
        if coordinate_form.is_valid() and form.is_valid():
            inst = coordinate_form.save()
            client.coordinates = inst
            form.save()
            return redirect(reverse("common_client_modify"))
    else:
        form = ClientForm(instance=client)
        coordinate_form = CoordinateForm(instance=coordinate)

    return render_to_response("common/client/modify.html", {
        "form": form,
        "coordinate_form": coordinate_form,
    }, context_instance=RequestContext(request))

@login_required
def trafiquable(request):
    if not request.is_ajax():
        return HttpResponse("This method may only be called via ajax")
    data = {}
    profile = request.user.get_profile()
    action = request.POST.get('action','get')
    id_table = request.POST.get('id_table',None)
    if id_table is None:
        data['error'] = u"Pas d'id table"
    else:
        if action == 'save':
            ordre_colonnes = json.loads(request.POST.get('liste_colonnes', None))
            if ordre_colonnes is None:
                data['error'] = u"Pas d'ordre_colonnes"
            else:
                profile.set_trafiquable(id_table, ordre_colonnes)
        elif action == 'get':
            data['ordre_colonnes'] = profile.get_trafiquable(id_table)
    if data.has_key('error') and data['error']:
        return HttpResponseBadRequest(json.dumps(data))
    return HttpResponse(json.dumps(data))

@login_required
def exportable(request):
    data = None
    result = {}
    if request.method != "POST":
        return HttpResponseBadRequest("Please use POST")
    else:
        data = request.POST.copy()
        action = data.get('action', 'exportcsv')
        csv    = data.get('data' , '')
        cle_table = data.get('cle_table', 'export')
        nomfichier = datetime.datetime.now().strftime(NOM_FICHIER_EXPORT) % (cle_table,)
        if action == "exportcsv":
            reponse = HttpResponse(content = csv, mimetype = "text/csv")
            reponse['Content-Disposition'] = 'attachment; filename=%s.csv' % (nomfichier,)
        elif action == "exportxls":
            from pyExcelerator import Workbook
            import tempfile
            tmpfile = tempfile.NamedTemporaryFile()
            wb = Workbook()
            ws0 = wb.add_sheet('0')
            for x, line in enumerate(csv.split("\n")):
                for y, cell in enumerate(line.split(";")):
                    ws0.write(x, y, cell)
            wb.save(tmpfile.name)
            reponse = HttpResponse(content = tmpfile.read(), mimetype = "application/vnd.ms-excel")
            tmpfile.unlink(tmpfile.name)
            reponse['Content-Disposition'] = 'attachment; filename=%s.xls' % (nomfichier,)
        elif action == "ftp":
            return communication.views.ftpsend(request,
                data = {
                    'dossier'  : '/tmp',
                    'filename' : '%s.csv' % (nomfichier,),
                    'data'     : csv,
                    }
                )
        elif action == "mail":
            return HttpResponse("mail")
        return reponse

