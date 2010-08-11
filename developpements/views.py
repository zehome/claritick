# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required

from django.utils.datastructures import SortedDict
from django.utils import simplejson as json

from developpements.models import Developpement, Version, Client, GroupeDev
from developpements.forms import DeveloppementForm

import traceback

@permission_required('developpements.can_access_suividev')
def home(request):
    return render_to_response("developpements/index.html", context_instance = RequestContext(request))

def prepare_liste_dev(request, project_id, shortlist = False):
    devs, couleurs = Developpement.objects.populate(project_id=project_id)
    clients = Developpement.client_demandeur.\
            through.objects.select_related("client", "client__client").filter(developpement__groupe__project__pk = project_id)
    versions = Version.contenu.through.\
            objects.select_related("version").filter(developpement__groupe__project__pk = project_id)

    # join devs clients and versions
    developpements = SortedDict()
    for d in devs:
        d.clients = []
        d.dispo_version = None
        developpements[d.pk] = d

    for c in clients:
        developpements[c.developpement.pk].clients.append(c.client)
    for v in versions:
        old = developpements[v.developpement.pk].dispo_version
        # overwrite ?
        if not old or old > v.version:
            developpements[v.developpement.pk].dispo_version = v.version
            developpements[v.developpement.pk].deja_dispo = "%s" % (v.version)
            developpements[v.developpement.pk].date_sortie = "%s" % (v.version.date_sortie)
    if shortlist:
        filtered_devs = SortedDict()
        for key, dev in developpements.items():
            if not dev.done and dev.version_requise:
                filtered_devs[key] = dev
        developpements = filtered_devs.values()
    else:
        developpements = developpements.values()
    versions_existantes = Version.objects.order_by('majeur','mineur','revision').values()

    return render_to_response("developpements/liste.html", {'developpements' : developpements, 'couleurs': couleurs, 'versions_existantes' : versions_existantes, 'project_id' : project_id}, context_instance = RequestContext(request))
    return developpements

@permission_required('developpements.can_view_liste')
def liste(request, project_id):
    return prepare_liste_dev(request, project_id)

@permission_required('developpements.can_view_liste')
def shortlist(request, project_id):
    return prepare_liste_dev(request, project_id, shortlist = True)

@permission_required('developpements.can_view_versions')
def versions(request, project_id):
    vers = Version.objects.filter(project__pk = project_id).order_by('majeur','mineur','revision')
    devs = Version.contenu.through.objects.select_related("developpement",
            "developpement__groupe", "developpement__version_requise").filter(developpement__groupe__project__pk = project_id)
    tous_devs, _ = Developpement.objects.populate(project_id=project_id)

    versions = SortedDict()
    for v in vers:
        v.content = []
        versions[v.pk] = v
    for d in devs:
        versions[d.version_id].content.append(d.developpement)

    versions = versions.values()

    dev_deja_sortis = []
    for ver in versions:
        ver.deja_sortie = False
        dev_contenus = ver.content
        if dev_contenus:
            ver.deja_sortie = True
            dev_deja_sortis.extend(dev_contenus)
        elif tous_devs:
            ver.date_sortie_complete = ver.date_sortie
            ver.contenu_sortie_prevue = []
            ver.contenu_sortie_retardee = []
            buffer = []
            for dev in tous_devs:
                if dev not in dev_deja_sortis and dev.date_sortie and ver.date_sortie and dev.date_sortie <= ver.date_sortie:
                    ver.contenu_sortie_prevue.append(dev)
                buffer.append(dev)
                if dev.version_requise == ver:# or (dev.engagement and ver.date_sortie and dev.engagement < ver.date_sortie):
                    if dev.date_sortie:
                        if (ver.date_sortie_complete and dev.date_sortie > ver.date_sortie_complete) or (ver.date_sortie_complete is None):
                            ver.date_sortie_complete = dev.date_sortie
                            ver.contenu_sortie_retardee.extend([d for d in buffer if d not in ver.contenu_sortie_prevue and d not in dev_deja_sortis])
                            buffer = []

    return render_to_response("developpements/versions.html", {'versions' : versions, 'project_id' : project_id}, context_instance = RequestContext(request))

@permission_required('developpements.change_developpement')
def change_color(request):
    dev_pk = request.GET.get('dev_pk', None)
    couleur = request.GET.get('couleur', '')
    try:
        dev = Developpement.objects.get(pk = dev_pk)
    except Developpement.DoesNotExist:
        return HttpResponse(json.dumps({'dev_pk' : dev_pk, 'error' : 'does not exist'}))
    if couleur:
        dev.couleur = couleur
        dev.save()
        return HttpResponse(json.dumps({'dev_pk' : dev_pk, 'couleur' : "%s" % (dev.couleur,)}))
    dev.couleur = ''
    dev.save()
    return HttpResponse(json.dumps({'dev_pk' : dev_pk}))

@permission_required('developpements.change_developpement')
def save_item_field(request):
    dev_pk = request.GET.get('dev_pk', None)
    field_type = request.GET.get('field_type', '')
    value_type = request.GET.get('value_type', 'integer')
    newvalue = request.GET.get('newvalue', '')
    result_dict = {'dev_pk' : dev_pk}
    old_poids_total = None
    try:
        if value_type == 'integer':
            newvalue = int(newvalue)
        elif value_type == 'float':
            newvalue = float(newvalue)
        try:
            dev = Developpement.objects.get(pk = dev_pk)
        except Developpement.DoesNotExist:
            result_dict['error'] = 'does not exist'
            return HttpResponse(json.dumps(result_dict))
        old_poids_total = dev.poids_total
        if not (field_type and newvalue):
            result_dict['error'] = 'No field or value'
            return HttpReponse(json.dumps(result_dict))
        if field_type not in ['temps_prevu','poids','poids_manuel','nom', 'poids_groupe', 'version_requise', ]:
            result_dict['error'] = 'Unknown field type %s' % (field_type,)
            return HttpResponse(json.dumps(result_dict))
        if field_type == 'poids_groupe':
            dev.groupe.poids = newvalue
            dev.groupe.save()
        elif field_type == 'version_requise':
            try:
                new_version = Version.objects.get(pk = newvalue)
            except Version.DoesNotExist:
                result_dict['error'] = 'Aucune version trouvee'
                return HttpResponse(json.dumps(result_dict))
            else:
                dev.version_requise = new_version
                dev.save()
                result_dict['innerHTML'] = '%s.%s.%s' % (new_version.majeur, new_version.mineur, new_version.revision,)
                return HttpResponse(json.dumps(result_dict))
        elif hasattr(dev, field_type):
            setattr(dev, field_type, newvalue)
            dev.save()
        else:
            result_dict['error'] = 'Dev does not have %s' % (field_type,)
            return HttpResponse(json.dumps(result_dict))
        if old_poids_total and dev.poids_total != old_poids_total:
            result_dict['new_poids_total'] = dev.poids_total
    except:
        result_dict['error'] = traceback.format_exc()
        return HttpResponse(json.dumps(result_dict))
    return HttpResponse(json.dumps(result_dict))

@permission_required('developpements.change_developpement')
def done(request):
    dev_pk = request.GET.get('dev_pk', None)
    try:
        dev = Developpement.objects.get(pk = dev_pk)
    except Developpement.DoesNotExist:
        return HttpResponse(json.dumps({'dev_pk' : dev_pk, 'error' : 'does not exist'}))
    if dev.done:
        dev.done = False
    else:
        dev.done = True
    dev.save()
    return HttpResponse(json.dumps({'dev_pk' : dev_pk}))

@permission_required('developpements.change_developpement')
def bug(request):
    dev_pk = request.GET.get('dev_pk', None)
    try:
        dev = Developpement.objects.get(pk = dev_pk)
    except Developpement.DoesNotExist:
        return HttpResponse(json.dumps({'dev_pk' : dev_pk, 'error' : 'does not exist'}))
    if dev.bug:
        dev.bug = False
    else:
        dev.bug = True
    dev.save()
    return HttpResponse(json.dumps({'dev_pk' : dev_pk}))

@permission_required("developpements.change_developpement")
def modify(request):
    """ modification dev en ajax, dev_pk = 0 -> nouveau dev """
    dev_pk = int(request.GET.get("dev_pk", request.POST.get("dev_pk", 0)))

    ret = {"itempk": dev_pk}

    if not dev_pk:
        dev = None
    else:
        dev = Developpement.objects.get(pk=dev_pk)

    if request.method == "POST":
        form = DeveloppementForm(request.POST, instance=dev, auto_id="id_modify_%s")
        if form.is_valid():
            form.save()
        else:
            ret["error"] = u"Il y a des érreurs dans le formulaire"
    else:
        form = DeveloppementForm(instance=dev, auto_id="id_modify_%s")

    ret["form"] = u"%s" % (form)

    return HttpResponse(json.dumps(ret))

@permission_required("developpements.change_developpement")
def populate_field(request):
    """ Renvoie les groupe & version en json pour un projet donné """
    project_pk = int(request.GET.get("project_pk", None))
    ret = {}

    if not project_pk:
        ret["error"] = u"Pas de projet spécifié"
    else:
        groupe = GroupeDev.objects.filter(project=project_pk)
        version = Version.objects.filter(project=project_pk)
        for key,val in zip(("groupe", "version"), [groupe, version]):
            ret[key] = [{"value": x.pk, "label": unicode(x)} for x in val]

    return HttpResponse(json.dumps(ret))

@permission_required("developpements.can_view_liste")
def dev_dialog(request, dev_pk):
    try:
        dev = Developpement.objects.get(pk = dev_pk)
    except Developpement.DoesNotExist:
        return HttpResponse("Ce dev n'existe pas")
    return render_to_response("developpements/dev_dialog.html", {"dev" : dev}, context_instance = RequestContext(request))
