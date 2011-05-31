# -*- coding: utf-8 -*-

from django.db import models

class EtiquetteTemplate(models.Model):
    title = models.CharField(u"titre", max_length=128)
    template = models.TextField(u"format d'étiquête", help_text="Note: l'instance traitée est accessible sous le nom 'instance'")
    printer_ip = models.CharField(u"IP de l'imprimante", max_length=128)
    app_name = models.CharField(u"Nom du module", help_text="Nom de module, Example: ticket", max_length=128, blank=True)
    model_name = models.CharField(u"Nom du modèle", help_text="doit avoir une méthode .have_permission(user). Example: Ticket", max_length=128, blank=True)

    class Meta:
        verbose_name = u"Modèle d'étiquette"
        ordering = [u'title',]
        permissions = (
            (u'print_etiquettetemplate',u"Imprimer templates d'étiquettes"),
        )

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.id)


