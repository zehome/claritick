# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required

from django.utils.datastructures import SortedDict
from django.utils import simplejson as json

from developpements.models import Developpement, Version, Client, GroupeDev
from developpements.forms import DeveloppementForm


@permission_required('developpements.can_access_suividev')
def home(request):
    return render_to_response("developpements/index.html", context_instance = RequestContext(request))

@permission_required('developpements.can_view_liste')
def liste(request, project_id):
    devs, couleurs = Developpement.objects.populate(project_id=project_id)
    clients = Developpement.client_demandeur.\
            through.objects.select_related("client", "client__client").all()
    versions = Version.contenu.through.\
            objects.select_related("version").all()

    # join devs clients and versions
    developpements = SortedDict()
    for d in devs:
        d.clients = []
        d.dispo_version = None
        developpements[d.pk] = d

    for c in clients:
        developpements[c.developpement_id].clients.append(c.client)
    for v in versions:
        old = developpements[v.developpement_id].dispo_version
        # overwrite ?
        if not old or old > v.version:
            developpements[v.developpement_id].dispo_version = v.version
            developpements[v.developpement_id].deja_dispo = "%s" % (v.version)
            developpements[v.developpement_id].date_sortie = "%s" % (v.version.date_sortie)
    developpements = developpements.values()

    return render_to_response("developpements/liste.html", {'developpements' : developpements, 'couleurs': couleurs}, context_instance = RequestContext(request))

@permission_required('developpements.can_view_versions')
def versions(request, project_id):
    vers = Version.objects.order_by('majeur','mineur','revision')
    devs = Version.contenu.through.objects.select_related("developpement",
            "developpement__groupe", "developpement__version_requise").all()
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

    return render_to_response("developpements/versions.html", {'versions' : versions}, context_instance = RequestContext(request))

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
def done(request):
    dev_pk = request.GET.get('dev_pk', None)
    try:
        dev = Developpement.objects.get(pk = dev_pk)
    except Developpement.DoesNotExist:
        return HttpResponse(json.dumps({'dev_pk' : dev_pk, 'error' : 'does not exist'}))
    if dev.done:
        return HttpResponse(json.dumps({'dev_pk' : dev_pk, 'error' : u'Déjà terminé'}))
    dev.done = True
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
