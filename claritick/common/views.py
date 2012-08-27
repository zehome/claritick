# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.utils import simplejson as json

from common.models import Client, Coordinate
from common.forms import ClientForm, CoordinateForm
from common.utils import user_has_perms_on_client
from bondecommande.models import BonDeCommande

try:
    from chuser.forms import ChuserForm
except ImportError:
    ChuserForm = None

# LC: XX: crossdependency: BAD
try:
    from packaging.models import ClientPackageAuth
except ImportError:
    print "Hummf"


@login_required
def infos_login(request):
    """
    Informations sur le client (liste d'enfants, modif mot de passe, ...)
    """
    client = request.user.my_userprofile.client
    if not client:
        raise Exception(u"Pas de client dans le profil pour l'utilisateur %s." % request.user)

    # First determine packageAuth client
    try:
        packageauth = ClientPackageAuth.objects.get(client__pk=client.id)
    except ClientPackageAuth.DoesNotExist:
        packageauth = None
    except NameError:  # LC: Import failed
        packageauth = None

    client_qs = Client.objects.get_childs('parent', client.pk)

    chuserform = None
    if request.user.is_superuser or request.session.get('was_superuser', False) and ChuserForm:
        chuserform = ChuserForm(initial={'user': request.user.pk})

    bondecommandes = BonDeCommande.objects.all().filter_by_user(request.user)

    return render_to_response("common/client/infos.html", {
        "client": client,
        "clients": client_qs,
        "packageauth": packageauth,
        "chuserform": chuserform,
        "bondecommandes": bondecommandes,
    }, context_instance=RequestContext(request))


@login_required
def modify_client(request, client_id):
    user_client = request.user.my_userprofile.client
    if not user_client:
        raise Exception(u"Pas de client dans le profil pour l'utilisateur %s." % request.user)

    client = get_object_or_404(Client, pk=client_id)
    if not user_has_perms_on_client(request.user, client):
        raise PermissionDenied

    coordinate = client.coordinates or Coordinate()
    if request.method == "POST":
        client_form = ClientForm(request.POST, instance=client)
        coordinate_form = CoordinateForm(request.POST, instance=coordinate)
        if coordinate_form.is_valid() and client_form.is_valid():
            inst = coordinate_form.save()
            client.coordinates = inst
            client_form.save()
            #return redirect(reverse("common.views.modify_client"))
    else:
        client_form = ClientForm(instance=client)
        coordinate_form = CoordinateForm(instance=coordinate)

    return render_to_response("common/client/modify.html", {
        "client": client,
        "client_form": client_form,
        "coordinate_form": coordinate_form,
    }, context_instance=RequestContext(request))


@login_required
def trafiquable(request):
    if not request.is_ajax():
        return HttpResponse("This method may only be called via ajax")
    data = {}
    profile = request.user.my_userprofile
    action = request.POST.get('action', 'get')
    id_table = request.POST.get('id_table', None)
    if id_table is None:
        data['error'] = u"Pas d'id table"
    else:
        if action == 'save':
            ordre_colonnes = \
                json.loads(request.POST.get('liste_colonnes', None))
            if ordre_colonnes is None:
                data['error'] = u"Pas d'ordre_colonnes"
            else:
                profile.set_trafiquable(id_table, ordre_colonnes)
        elif action == 'get':
            data['ordre_colonnes'] = profile.get_trafiquable(id_table)
    if data.get('error'):
        return HttpResponseBadRequest(json.dumps(data))
    return HttpResponse(json.dumps(data))
