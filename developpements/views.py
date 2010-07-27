# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required

from django.utils.datastructures import SortedDict
from django.utils import simplejson as json

from developpements.models import Developpement, Version, Client
import datetime

FORCE_DEV = 55 # heures par semaine

def week_start_date(year, week):
    d = datetime.date(year, 1, 1)
    delta_days = d.isoweekday() - 1
    delta_weeks = week
    if year == d.isocalendar()[0]:
        delta_weeks -= 1
    delta = datetime.timedelta(days = -delta_days, weeks = delta_weeks)
    return d + delta

@permission_required('developpements.can_access_suividev')
def home(request):
    return render_to_response("developpements/index.html", context_instance = RequestContext(request))

@permission_required('developpements.can_view_liste')
def liste(request):
    devs = Developpement.objects.all()
    clients = Developpement.client_demandeur.\
            through.objects.select_related("client").all()
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

    developpements = developpements.values()
    now = datetime.datetime.now()
    semaine_en_cours = now.isocalendar()[1] + 1
    heures_dev = 0
    couleurs = []

    for dev in developpements:
        if dev.couleur and not dev.couleur in couleurs:
            couleurs.append(dev.couleur)
        dev.date_sortie = None
        if dev.done:
            semaine = semaine_en_cours + (heures_dev / FORCE_DEV)
            dev.date_sortie = week_start_date(now.year, int(semaine))
        elif dev.temps_prevu:
            heures_dev = heures_dev + dev.temps_prevu
            semaine = semaine_en_cours + (heures_dev / FORCE_DEV)
            dev.date_sortie = week_start_date(now.year, int(semaine))
        if dev.groupe.version_requise:
            if dev.version_requise:
                if dev.version_requise.majeur > dev.groupe.version_requise.majeur:
                    dev.version_requise = dev.groupe.version_requise
                elif dev.version_requise.majeur == dev.groupe.version_requise.majeur and dev.version_requise.mineur > dev.groupe.version_requise.mineur:
                    dev.version_requise = dev.groupe.version_requise
            else:
                dev.version_requise = dev.groupe.version_requise
        if isinstance(dev.date_sortie, datetime.datetime):
            dev.date_sortie = dev.date_sortie.date()
        if isinstance(dev.engagement, datetime.datetime):
            dev.engagement = dev.engagement.date()
        if dev.dispo_version:
            dev.deja_dispo = "%s" % (dev.dispo_version,)
            dev.date_sortie = dev.dispo_version.date_sortie
        if not dev.done:
            if dev.date_sortie and dev.engagement and dev.date_sortie > dev.engagement:
                dev.alerte = u"Date de sortie prévue dépasse la date d'engagement"
            if not dev.date_sortie:
                dev.alerte = u"Pas de date sortie calculable pour ce dev"
            elif dev.version_requise and dev.version_requise.date_sortie and dev.date_sortie > dev.version_requise.date_sortie:
                dev.alerte = u"Date de sortie prévue dépasse la date de sortie de la version"
    
    request.session["developpements"] = developpements
        
    return render_to_response("developpements/liste.html", {'developpements' : developpements, 'couleurs': couleurs}, context_instance = RequestContext(request))

@permission_required('developpements.can_view_versions')
def versions(request):
    versions = list(Version.objects.order_by('majeur','mineur'))
    dev_deja_sortis = []
    tous_dev = request.session.get("developpements", None)
    if not tous_dev:
        # Appel à la vue liste qui va générer l'object en session
        liste(request)
    tous_dev = request.session.get("developpements", None)
    for ver in versions:
        ver.deja_sortie = False
        dev_contenus = ver.contenu.all()
        if dev_contenus:
            ver.deja_sortie = True
            dev_deja_sortis.extend(dev_contenus)
        elif tous_dev:
            ver.date_sortie_complete = ver.date_sortie
            ver.contenu_sortie_prevue = []
            ver.contenu_sortie_retardee = []
            buffer = []
            for dev in tous_dev:
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
