# -*- coding: utf-8 -*-

class NoProfileException(Exception):
    
    def __init__(self, user):
        self.args = (u"Erreur de paramétrage : l'utilisateur %s n'a pas de profil." % user, )
