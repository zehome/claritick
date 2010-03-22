# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.comments.moderation import CommentModerator, moderator
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted, comment_will_be_posted
from django.contrib.contenttypes.models import ContentType

# for email
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context, Template

# Clarisys fields
from claritick.common.models import ColorField, Client, ClientField
from claritick.common.widgets import ColorPickerWidget 
from django.db.models import AutoField


def copy_model_instance(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and\
                       not f in obj._meta.parents.values()])
    return obj.__class__(**initial)

class Priority(models.Model):
    class Meta:
        verbose_name = "Priorité"
        ordering = ['warning_duration', 'label']

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
        ordering = ['weight', 'label']

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
        ordering = ['label']

    label = models.CharField("Libellé", max_length=64)
    
    def __unicode__(self):
        return u"%s" % (self.label,)

class Project(models.Model):
    class Meta:
        verbose_name = u"Projet"
        ordering = ['label']
    
    label = models.CharField("Libellé", max_length=64)
    color = ColorField(name="Couleur associée", blank=True, null=True)
    #watchers = models.ManyToManyField(User, blank=True)
    procedure = models.ForeignKey('Procedure', verbose_name=u'Procédure', limit_choices_to={'active': True}, blank = True, null = True)
    
    def __unicode__(self):
        if self.procedure:
            return u"%s (%s)" % (self.label, self.procedure)
        return u"%s" % self.label 
    
    def save(self, client_id=None):
        """ Override save in order to pass "client" from ModelAdmin form """
        created = bool(not self.id)
        r = super(Project, self).save()
        if created:
            # Ajoute les tickets correspondant a la procédure
            if self.procedure:
                for ticketOriginal in self.procedure.tickets.all():
                    ticket = copy_model_instance(ticketOriginal)
                    ticket.date_open = None
                    ticket.template = False
                    ticket.project = self
                    if client_id and not ticket.client:
                        ticket.client = Client.objects.get(pk=int(client_id))
                    
                    ticket.save()        
        return r

class Procedure(models.Model):
    class Meta:
        verbose_name = u"Procédure"
        ordering = ['label']

    label = models.CharField("Libellé", max_length=64)
    active = models.BooleanField()
    category = models.ForeignKey(Category, verbose_name="Catégorie")
    tickets = models.ManyToManyField('Ticket', verbose_name="Ticket", limit_choices_to={'template': True})
    
    def __unicode__(self):
        return u"%s" % (self.label,)

class TicketManager(models.Manager):
    def get_query_set(self):
        qs = super(TicketManager, self).get_query_set()
        qs = qs.filter(text__isnull=False)
        qs = qs.exclude(template__exact=True)
        return qs

class OpenTicketManager(TicketManager):
    def get_query_set(self):
        qs = super(OpenTicketManager, self).get_query_set()
        qs = qs.exclude(state__id__in = (0,4))
        return qs
    
class Ticket(models.Model):
    class Meta:
        verbose_name = "Ticket"
        ordering = ['-last_modification']
        permissions = (
            ("can_view_report", "Consulter les rapports"),
        )
    
    objects = models.Manager()
    tickets = TicketManager()
    open_tickets = OpenTicketManager()

    # Info client
    client = ClientField(Client, verbose_name="Client", blank=True, null=True)
    contact = models.CharField("Contact", max_length=128, blank=True)
    telephone = models.CharField("Téléphone", max_length=20, blank=True)
    
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
    keywords = models.CharField("Mots clefs", max_length=1024, blank=True, null=True)
    
    # Calendar
    calendar_start_time = models.DateTimeField("Début évenement", blank=True, null=True)
    calendar_end_time = models.DateTimeField("Fin évenement", blank=True, null=True)
    calendar_title = models.CharField("Titre évenement", max_length=64, blank=True, null=True)
    
    template = models.BooleanField("Modèle", default=False)
    
    # Used for "reporting" tool
    @property
    def reporting_state_open(self):
        return self.state and (self.state.id in (1,2,3) and 1 or 0) or 0
    @property
    def reporting_state_closed(self):
        return self.state and (self.state.id == 4 and 1 or 0) or 0
    @property
    def reporting_priority_low(self):
        return self.priority and (self.priority.id == 1 and 1 or 0) or 0
    @property
    def reporting_priority_normal(self):
        return self.priority and (self.priority.id == 2 and 1 or 0) or 0
    @property
    def reporting_priority_high(self):
        return self.priority and (self.priority.id == 3 and 1 or 0) or 0
    @property
    def reporting_priority_critical(self):
        return self.priority and (self.priority.id == 4 and 1 or 0) or 0
    
    @property
    def close_style(self):
        if self.date_close or self.state.id == 4:
            return "text-decoration: line-through;"
        return ""
    
    @property
    def priority_text_style(self):
        style = ""
        if self.priority:
            p = self.priority
            if p.forecolor:
                style += "color: %s;" % (p.forecolor,)
        return style
    
    @property
    def priority_back_style(self):
        style = ""
        p = self.priority
        if p:
            if p.backcolor:
                style += "background-color: %s;" % (p.backcolor,)
        return style
    
    def is_valid(self):
        return bool(self.text and self.title)
    
    def get_absolute_url(self):
        return "/ticket/modify/%i" % (self.id,)
    
    def __unicode__(self):
        return u"n°%s: %s" % (self.id, self.title) 

    @staticmethod
    def handle_comment_posted_signal(sender, **kwargs):
        """ Updates ticket last_modification to now() """
        comment = kwargs["comment"]
        if comment.content_type.model != "ticket":
            return
        
        ticket = comment.content_object
        ticket.last_modification=datetime.datetime.now()
        ticket.save()
        
        # Send email
        ticket.send_email(reasons = [ u"Nouvelle réponse", ])
    
    @staticmethod
    def handle_ticket_presave_signal(sender, **kwargs):
        new_ticket = kwargs["instance"]
        if not new_ticket.id:
            return
        
        from claritick import get_observer
        try:
            old_ticket = Ticket.objects.get(id=new_ticket.id)
        except Ticket.DoesNotExist:
            return
        if old_ticket.assigned_to and old_ticket.assigned_to != new_ticket.assigned_to:
            # Vérif ya t'il un google event ?
            observer = get_observer(old_ticket.assigned_to)
            if observer:
                e = observer.get_event(observer.service, old_ticket)
                if e:
                    observer.delete(Ticket, old_ticket)

    def save(self):
        """ Overwrite save in order to do checks if email should be sent, then send email """
        send_email_reason=None
        
        try:
            old_ticket = Ticket.objects.get(id=self.id)
        except Ticket.DoesNotExist:
            old_ticket = None
        
        r = super(Ticket, self).save()
        
        send_fax_reasons = []
        send_email_reasons = []
        if self.is_valid():
            if old_ticket is None:
                r = u"Création du ticket"
                send_email_reasons = [ r, ]
                senf_fax_reasons = [ r, ]
            else:
                if old_ticket.state and old_ticket.state != self.state:
                    r = u"Status modifié: %s => %s" % (old_ticket.state, self.state)
                    send_email_reasons.append(r)
                    send_fax_reasons.append(r)
                if old_ticket.client and old_ticket.client != self.client:
                    r = u"Erreur d'affectation client"
                    send_email_reasons.append(r)
                    senf_fax_reasons.append(r)
                if old_ticket.validated_by is None and self.validated_by:
                    send_email_reasons.append(u"Ticket accepté par %s" % (self.validated_by,))
                if (old_ticket.assigned_to and old_ticket.assigned_to != self.assigned_to):
                    send_email_reasons.append(u"Ticket re-affecté à %s" % (self.assigned_to,))
                elif (not old_ticket.assigned_to and self.assigned_to):
                    send_email_reasons.append(u"Ticket affecté à %s" % (self.assigned_to,))
        
        if send_email_reasons:
            self.send_email(send_email_reasons)
        
        if send_fax_reasons:
            self.send_fax(send_fax_reasons)
        
        return r
    
    def send_fax(self, reasons=[u'Demande spécifique']):
        """ Send a fax for this particuliar ticket """
        faxes = set(self.client.get_faxes())
        
        if self.client and self.client.notifications_by_fax:
            print "send_fax to %s reasons: %s" % (faxes, reasons,)
        else:
            print "no send_fax: le client ne veut pas être faxé"
    
    def send_email(self, reasons=[u"Demande spécifique",]):
        """ Send an email for this particuliar ticket """
        dests = set()
        if self.client:
            dests.union(set(self.client.get_emails()))
        
        # La personne qui a ouvert
        if self.opened_by.email:
            dests.add(self.opened_by.email)
        
        # La personne sur qui le ticket est assignée
        if self.assigned_to and self.assigned_to.email:
            dests.add(self.assigned_to.email)
        
        # Les project watchers ?
        # LC: TODO watchers
        
        # Ceux qui ont participé (comments)
        dests.union( set([ c.user.email for c in Comment.objects.for_model(self) if c.user and c.user.email ]))
        
        print "Envoi d'email à %s. Raisons: %s" % (dests, reasons)
        if not dests:
            print "Aucun destinataire email ?!"
            return
        
        # Application du template email
        template = get_template("email/ticket.txt")
        context = Context({"ticket": self, 'reasons': reasons })
        data = template.render(context)
        
        template = Template("[Ticket {{ ticket.id }}]: {{ ticket.title|striptags|truncatewords:64 }}")
        subject = template.render(context)
        # Send the email
        send_mail(subject, data, u"support@clarisys.fr", dests)
        
# Update last_modification time
comment_was_posted.connect(Ticket.handle_comment_posted_signal)

# Google calendar sync
models.signals.pre_save.connect(Ticket.handle_ticket_presave_signal, sender=Ticket)

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
