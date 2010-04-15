# -*- coding: utf-8 -*-

from django.core.management import base
from django.db.models import Q

from common.models import *
from clariadmin.models import *
import djangodialog as D

def dialog_clariadmin():
    default_text_filter = ""
    
    while True:
        ret = D.dialog_inputbox("Filtrage machine (hostname, ip, serial, automate)", default_text_filter)
        if ret[0]: # Cancel:
            break
        
        default_text_filter = ret[1]
        query = Q(hostname__istartswith=ret[1]) | Q(ip__icontains=ret[1]) | Q(serial__iexact=ret[1]) | Q(automate__icontains=ret[1])
        hosts = Host.objects.filter(query)
        if not hosts:
            D.dialog_msgbox("Aucun résultat")
        else:
            choices = [ (str(h.id), str(h)) for h in hosts ]
            ret = D.dialog_menu("Machine (Filtrage: %s)" % (ret[1],), choices)
            if ret[0]:
                continue
            else:
                host = Host.objects.get(pk=int(ret[1]))
                
                actions = [ ('voir', 'Consulter'), ('ssh', 'Accéder en SSH'), ]
                ret = D.dialog_menu("Que souhaitez vous faire sur %s ?" % (host,), actions)
                if ret[0]:
                    continue
                if ret[1] == 'voir':
                    D.dialog_msgbox(host.get_text())
                elif ret[1] == 'ssh':
                    D.dialog_msgbox("Pas encore implémenté.")
                else:
                    D.dialog_msgbox("Hein ??")

class Command(base.BaseCommand):
    def handle(self, **kwargs):
        choices = [ ("clariadmin", "Recherche CLARIADMIN"), ]
        
        while True:
            ret = D.dialog_menu("Choix de l'application", choices)
            if ret[0]: # Cancel:
                print "See you soon!"
                break
            
            if ret[1] == 'clariadmin':
                dialog_clariadmin()
