# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
#~ from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

import os

register = template.Library()

MEDIA_URL = getattr(settings, "MEDIA_URL", "/site_media/")

@register.filter
def startswith(value, arg):
    "Renvoie vrai si la chaîne commence par l'argument"
    return value.startswith(arg)

@register.filter
def cesure(value, arg):
    """
    Coupe la chaîne en morceaux composés de mots entiers sans dépasser un maximum de 'arg' lettres
    """
    
    def prendre_morceau(mots, longueur):
        if not mots:
            return "",[]
        result = [mots.pop(0),]
        while len(" ".join(result)) < longueur and mots:
            result.append(mots.pop(0))
        if len(result) > 1 and len(" ".join(result)) > longueur:
            mots.insert(0, result.pop())
        result = " ".join(result)
        return result, mots

    lignes = value.split("\n")
    resultat_complet = []
    for ligne in lignes:
        result = []
        mots = ligne.split()
        while mots:
            morceau, mots = prendre_morceau(mots, arg)
            result.append(morceau)
        resultat_complet.append("\n".join(result))
    return mark_safe("\n".join(resultat_complet))


@register.simple_tag
def setting(name, default = ""):
    return getattr(settings, name, default)
