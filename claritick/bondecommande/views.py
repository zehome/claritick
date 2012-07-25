# -*- coding: utf-8 -*-

from django import http
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from bondecommande.models import BonDeCommande, BonDeCommandeFile

@login_required
def getfile(request, file_id):
    """
    Retourne le fichier du bon de commande
    """
    file = get_object_or_404(BonDeCommandeFile.with_data, pk=file_id)

    if not BonDeCommande.objects.all().filter_by_user(request.user).get(pk=file.bondecommande_id):
        raise PermissionDenied

    response = http.HttpResponse(str(file.data), mimetype=file.content_type)
    try:
        response["Content-Disposition"] = "attachment; filename=%s" % (file.filename,)
    except UnicodeEncodeError:
        ext = file.filename.split(".")[-1]
        response["Content-Disposition"] = "attachment; filename=fichier%s.%s" % (file_id, ext)
        
    return response