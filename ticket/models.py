# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.comments.moderation import CommentModerator, moderator

# Clarisys fields
from claritick.common.models import ColorField, Client, ClientField
from claritick.common.widgets import ColorPickerWidget 


class Priority(models.Model):
    class Meta:
        verbose_name = "Priorité"

    label = models.CharField("Libellé", max_length=64, blank=True)
    forecolor = ColorField("Couleur du texte", blank=True)
    backcolor = ColorField("Couleur de fond", blank=True)
    
    good_duration = models.IntegerField("Durée en seconde => Bon", blank=True, null=True)
    warning_duration = models.IntegerField("Durée en seconde => Attention", blank=True, null=True)
    critical_duration = models.IntegerField("Durée en seconde => Critique", blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.label,)

class State(models.Model):
    class Meta:
        verbose_name = "État"
        verbose_name_plural = "État"

    label = models.CharField("Libellé", max_length=64)
    weight = models.IntegerField("Poids", default=1)

    def __unicode__(self):
        return u"%s" % (self.label,)

class Category(models.Model):
    """

    Exemple: Admin, Formation, Support, Développement, TODO
    """
    class Meta:
        verbose_name = "Catégorie"

    label = models.CharField("Libellé", max_length=64)
    
    def __unicode__(self):
        return u"%s" % (self.label,)

class Project(models.Model):
    class Meta:
        verbose_name = "Projet"
    label = models.CharField("Libellé", max_length=64)
    color = ColorField(name="Couleur associée", blank=True, null=True)
    watchers = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        return u"%s watched by [%s]" % (self.label, ",".join([ u.username for u in self.watchers.all() ]))

class Ticket(models.Model):
    class Meta:
        verbose_name = "Ticket"

    # Numero = id
    
    # Info client
    client = ClientField(Client, verbose_name="Client", blank=True, null=True)
    contact = models.CharField("Contact", max_length=128, blank=True)
    telephone = models.CharField("Téléphone", max_length=10, blank=True)
    
    date_open = models.DateTimeField("Date d'ouverture", auto_now_add=True)
    last_modification = models.DateTimeField("Dernière modification", auto_now_add=True,auto_now=True)
    date_close = models.DateTimeField("Date de fermeture", blank=True, null=True)

    state = models.ForeignKey(State, verbose_name="État", blank=True, null=True)
    priority = models.ForeignKey(Priority, verbose_name="Priorité", blank=True, null=True)

    assigned_to = models.ForeignKey(User, related_name = "assigned_to", verbose_name="Assigné à", blank=True, null=True)
    opened_by = models.ForeignKey(User, related_name="opened_by", verbose_name="Ouvert par")
    title = models.CharField("Titre", max_length=128, blank=True, null=True)
    text = models.TextField("Texte", blank=True, null=True)

    category = models.ForeignKey(Category, verbose_name="Catégorie")
    project = models.ForeignKey(Project, verbose_name="Projet", blank=True, null=True)

    # Si le ticket est d'une provenance extérieure, alors validated_by
    # ne sera pas défini. Il faudra qu'un "clarimen" Valide le ticket
    validated_by = models.ForeignKey(User, related_name="validated_by", verbose_name="Validé par", blank=True, null=True, default=None)
    
    # Pour faciliter la recherche
    keywords = models.CharField("Mots clefs", max_length=1024, blank=True)
    
    # Calendar
    calendar_start_time = models.DateTimeField("Début évenement", blank=True, null=True)
    calendar_end_time = models.DateTimeField("Fin évenement", blank=True, null=True)
    calendar_title = models.CharField("Titre évenement", max_length=64, blank=True, null=True)
    
    def get_groupement(self):
        """ Retourne le groupement associé au ticket """
        if self.site:
            return self.site.groupement
        else:
            if self.groupement:
                return self.groupement
        return None
    
    def is_valid(self):
        return bool(self.text and self.title)
    
    def __unicode__(self):
        return u"Ticket %s [%s] for %s prio: %s status: %s" % (self.id, self.category, self.get_groupement(), self.priority, self.state) 
    
## Ticket moderation
class TicketCommentModerator(CommentModerator):
    email_notification = False
    enable_field = 'enable_comments'
    
    def moderate(comment, content_object, request):
        """ Moderation for all non staff people is required. """
        if user and user.is_staff:
            return False
        return True
    
#moderator.register(Ticket, TicketCommentModerator)
