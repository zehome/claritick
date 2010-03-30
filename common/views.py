# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from common.models import Client, Coordinate
from common.forms import ClientForm, CoordinateForm

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
