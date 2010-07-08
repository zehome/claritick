# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.comments.moderation import CommentModerator, moderator
import django.contrib.comments
from django.contrib.comments.signals import comment_was_posted
from django.core.exceptions import ValidationError, FieldError

# for email
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context, Template

# Clarisys fields
from common.models import ColorField, Client, ClientField, JsonField, ByteaField, PickleField, UserProfile
from common.exceptions import NoProfileException
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
    alarm = models.CharField("Alarme automatique", max_length=128, null=True)
    
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
    img = models.FileField(upload_to='images/states', blank=True, null=True)

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


class TicketQuerySet(models.query.QuerySet):
    def add_order_by(self, request):
        sort = request.GET.get('sort', 'id')
        sort_order = int(request.GET.get('sort_order', 1))
        return self.order_by('%s%s' % (sort_order and '-' or '', sort))

    def filter_ticket_by_user(self, user, **kwargs):
        """
            Filtre un queryset de ticket en fonction des clients qu'a le droit de voir l'utilisateur.
            kwargs:
                -> no_client à True accepte les ticket sans client
        """

        no_client = kwargs.pop("no_client", False)

        # Si on est root, on ne filtre pas la liste
        if user.is_superuser:
            return self
        qs = Ticket.objects.none()
        try:
            clients = user.get_profile().get_clients()
            query = models.Q(client__in=clients)

            if no_client:
                query |= models.Q(client__isnull=True)

            qs = self.filter(query)
        except UserProfile.DoesNotExist:
            raise NoProfileException(user)
        return qs

    def filter_queryset(self, filters, *args, **kwargs):
        """ Filtre un queryset de ticket a partir d'un dictionnaire de fields lookup. """
        search_mapping = {
            'title': 'icontains',
            'text': 'icontains',
            'contact': 'icontains',
            'keywords': 'icontains',
            'client': None,
        }

        qs = self.all()
        d = {}
        for key, value in filters.items():
            try:
                if value:
                    try:
                        lookup = search_mapping[key]
                    except KeyError:
                        if isinstance(value, (list, models.query.QuerySet)):
                            lookup = "in"
                        else:
                            lookup = 'exact'
                    if lookup is None:
                        continue
                    qs = qs.filter_or_child({"%s__%s"%(str(key), lookup): value}, *args, **kwargs)
            except (AttributeError, FieldError):
                pass

        client = filters.get("client", None)

        if client:
            # Traitement des lookup None
            clients = Client.objects.get_childs("parent", int(client))
            qs = qs.filter(client__in=[ c.id for c in clients ])

        return qs

    def filter_or_child(self, filter, user=None):
        """ Filtre suivant filterdict avec un OR sur les fils
        ne renvoie que le pêre si un fils matche filterdict """
        qs = self.all()

        child_condition = models.Q(child__isnull=False)

        # Matcher sur les fils qui ne sont pas en diffusion ?
        if user and not user.has_perm("ticket.can_list_all"):
            child_condition &= models.Q(child__diffusion=True)

        if isinstance(filter, models.query_utils.Q):
            query = models.Q()
            for k,v in filter.children:
                query |= models.Q(**{'child__%s'%k: v})
            qs = qs.filter(filter | \
                (child_condition & query))
        else:
            for k,v in filter.items():
                qs = qs.filter(models.Q(**{k: v}) | \
                        (child_condition & \
                        models.Q(**{"child__%s"%k: v})))
        return qs.distinct()

class QuerySetManager(models.Manager):
    def get_query_set(self):
        return TicketQuerySet(self.model)

class BaseTicketManager(QuerySetManager):
    def get_query_set(self):
        qs = super(BaseTicketManager, self).get_query_set().\
            select_related("opened_by", "assigned_to",
            "priority", "state", "validated_by", "category", "project",
            "client", "client__coordinates", "client__parent", "client__parent__coordinates", "client__parent__parent")
        return qs

class TicketManager(BaseTicketManager):
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
            ("can_view_report", u"Consulter les rapports"),
            ("add_ticket_full", u"Peut creer des tickets complet"),
            ("can_resolve", u"Peut resoudre des tickets"),
            ("can_list_all", u"Peut voir la liste détaillée"),
            ("can_validate_ticket", u"Peut valider un ticket"),
            ("can_add_child", u"Peut créer un ticket fils"),
            ("can_view_internal_comments", u"Peut voir les commentaires internes"),
        )


    minimal = QuerySetManager()
    objects = BaseTicketManager()
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
    keywords = models.CharField(u"Mots clefs", max_length=1024, blank=True, null=True)
    
    # Calendar
    calendar_start_time = models.DateTimeField(u"Début évenement", blank=True, null=True)
    calendar_end_time = models.DateTimeField(u"Fin évenement", blank=True, null=True)
    calendar_title = models.CharField(u"Titre évenement", max_length=64, blank=True, null=True)
    
    template = models.BooleanField(u"Modèle", default=False)

    # parent ticket
    parent = models.ForeignKey('Ticket', related_name="child", verbose_name="Ticket parent", blank=True, null=True)
    diffusion = models.BooleanField(default=True)

    # TODO nombre de comments
    nb_comments = models.IntegerField(default=0, editable=False)

    nb_appels = models.IntegerField(default=0, editable=False)

    # Par defaut à false
    update_google = False

    # Used for "reporting" tool
    @property
    def reporting_state_open(self):
        return self.state and (self.state.id in (1,2,3) and 1 or 0) or 0
    @property
    def reporting_state_closed(self):
        return self.state and (self.state.id == settings.TICKET_STATE_CLOSED and 1 or 0) or 0
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
    def is_closed(self):
        return self.date_close or self.state.id == settings.TICKET_STATE_CLOSED
    
    @property
    def close_style(self):
        if self.is_closed:
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

    def get_current_alarm(self):
        """ Renvoie l'alarme courante si elle existe sinon None """
        try:
            ret = TicketAlarm.opened.get(ticket=self)
        except TicketAlarm.DoesNotExist:
            ret = None
        return ret
    
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
        ticket.nb_comments = django.contrib.comments.get_model().objects.filter(content_type__model="ticket", object_pk=ticket.pk).count()
        ticket.save()
        
        # Send email
        if ticket.diffusion and (((not comment.internal) or 
            (comment.internal and getattr(settings, "EMAIL_INTERNAL_COMMENTS", True)))):
            send_email_reasons = [ u"Nouvelle réponse%s" % (comment.internal and " (Diffusion interne seulement)" or ''), ]
            #ticket.send_email(reasons=send_email_reasons)
            ticket.ticketmailaction_set.create(reasons=send_email_reasons)
    
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

    def clean(self):
        if self.state_id == settings.TICKET_STATE_CLOSED and self.child.exclude(state=self.state).exists():
            raise ValidationError("Impossible de fermer le ticket si tous les tickets fils ne sont pas fermés")

    def save(self):
        """ Overwrite save in order to do checks if email should be sent, then send email """
        send_email_reason=None

        try:
            old_ticket = Ticket.objects.get(id=self.id)
        except Ticket.DoesNotExist:
            old_ticket = None

        # Override date_close
        if old_ticket:
            if not old_ticket.is_closed and self.is_closed:
                self.date_close = datetime.datetime.now()
            # PP: On ne peux pas changer date_closed
            # if old_ticket.is_closed and not self.is_closed
            if old_ticket.is_closed and self.state_id != settings.TICKET_STATE_CLOSED:
                self.date_close = None

        r = super(Ticket, self).save()
        send_fax_reasons = []
        send_email_reasons = []

        if self.is_valid():
            if old_ticket is None:
                r = u"Création du ticket"
                send_email_reasons = [ r, ]
                send_fax_reasons = [ r, ]
            else:
                if old_ticket.state and old_ticket.state != self.state:
                    r = u"Status modifié: %s => %s" % (old_ticket.state, self.state)
                    send_email_reasons.append(r)
                    send_fax_reasons.append(r)
                if old_ticket.client and old_ticket.client != self.client:
                    r = u"Erreur d'affectation client"
                    send_email_reasons.append(r)
                    send_fax_reasons.append(r)
                if old_ticket.validated_by is None and self.validated_by:
                    send_email_reasons.append(u"Ticket accepté par %s" % (self.validated_by,))
                if (old_ticket.assigned_to and old_ticket.assigned_to != self.assigned_to):
                    if old_ticket.assigned_to and self.assigned_to and old_ticket.assigned_to.pk != self.assigned_to.pk:
                        send_email_reasons.append(u"Ticket re-affecté à %s" % (self.assigned_to,))
                elif (not old_ticket.assigned_to and self.assigned_to):
                    send_email_reasons.append(u"Ticket affecté à %s" % (self.assigned_to,))

            # Copie des paramêtres du père à reporter sur les fils
            # (Temporaire ?)
            if old_ticket and self.child:
                if old_ticket.priority != self.priority:
                    self.child.exclude(priority=self.priority).update(priority=self.priority)
                if old_ticket.client != self.client:
                    self.child.exclude(client=self.client).update(client=self.client)
                if old_ticket.contact != self.contact:
                    self.child.exclude(contact=self.contact).update(contact=self.contact)
                if old_ticket.telephone != self.telephone:
                    self.child.exclude(telephone=self.telephone).update(telephone=self.telephone)
                # PP: TODO Optimiser...
                for c in self.child.all():
                    c.save()

            # Si on change le paramètre diffusion de "True" vers "False",
            # On ne veut pas envoyer les emails en file d'attente!
            if old_ticket and old_ticket.diffusion and not self.diffusion:
                self.ticketmailtrace_set.all().delete()

        if self.parent:
            send_email_reasons = ["Ticket enfant %d : %s" % (self.pk, string) for string in send_email_reasons]
            send_fax_reasons = ["Ticket enfant %d : %s" % (self.pk, string) for string in send_fax_reasons]
            target_ticket = self.parent
        else:
            target_ticket = self

        if self.diffusion:
            if send_email_reasons:
                # LC: Do not send the email right now, wait some time before for grouping actions.
                #self.send_email(send_email_reasons)
                target_ticket.ticketmailaction_set.create(reasons=send_email_reasons)
            if send_fax_reasons:
                target_ticket.send_fax(send_fax_reasons)

        return r


    def send_fax(self, reasons=[u'Demande spécifique']):
        """ Send a fax for this particuliar ticket """
        if self.client is not None:
            faxes = set(self.client.get_faxes())
            
            #if self.client and self.client.notifications_by_fax:
            #    print "send_fax to %s reasons: %s" % (faxes, reasons,)
            #else:
            #    print "no send_fax: le client ne veut pas être faxé"
    
    def send_email(self, reasons=[u"Demande spécifique",]):
        """ Send an email for this particuliar ticket """
        dests = set()
        if self.client:
            dests = dests.union(set(self.client.get_emails()))

        # La personne qui a ouvert
        if self.opened_by.email:
            dests.add(self.opened_by.email)
        
        # La personne sur qui le ticket est assignée
        if self.assigned_to and self.assigned_to.email:
            dests.add(self.assigned_to.email)
        
        # Les project watchers ?
        # LC: TODO watchers
        
        # Ceux qui ont participé (comments)
        dests = dests.union( set([ c.user.email for c in django.contrib.comments.get_model().objects.filter(content_type__model="ticket", object_pk=str(self.id)) if c.user and c.user.email ]))
        
        #print "Envoi d'email à %s. Raisons: %s" % (dests, reasons)
        if not dests:
        #    print "Aucun destinataire email ?!"
            return
        
        # Application du template email
        template = get_template("email/ticket.txt")
        context = Context({"ticket": self, 'childs': self.child.order_by('date_open'), 'reasons': reasons })
        data = template.render(context)
        
        template = Template("{% autoescape off %}[Ticket {{ ticket.id }} ({{ ticket.state }})]: {{ ticket.title|striptags|truncatewords:64 }}{% endautoescape %}")
        subject = template.render(context)

        # Send the email
        mail = EmailMessage(subject, data, settings.DEFAULT_FROM_EMAIL, dests)
        self.ticketmailtrace_set.create(email=mail)
        mail.send()

class TicketView(models.Model):
    """
        Represente un ensemble de critere de recherches.
    """
    user = models.ForeignKey(User)
    name = models.TextField(default=u"Nom de la vue")
    filters = JsonField()

    class Meta:
        verbose_name = u"Vue"

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.user)

class TicketFile(models.Model):
    """
        Pièces jointe attachées aux tickets.
    """
    ticket = models.ForeignKey(Ticket)
    filename = models.TextField()
    content_type = models.TextField()
    data = ByteaField()

class TicketMailAction(models.Model):
    class Meta:
        permissions = (
            ("can_delete_tma", u"Peut supprimer des ticket mail action"),
        )
        ordering = ["date"]
    """
    
    Une action d'envoie d'email a faire plus tard
    """
    
    date = models.DateTimeField(verbose_name = u"Date d'ajout", auto_now_add = True, blank=False)
    reasons = PickleField(blank=False)
    ticket = models.ForeignKey(Ticket)

    class Meta:
        verbose_name = u"Email à envoyer"
        verbose_name_plural = u"Emails à envoyer"
    
    def __unicode__(self):
        return u"Email pour ticket %s à envoyer" % (self.ticket.id,)

class TicketMailTrace(models.Model):
    """
        Trace des mails envoyés par tickets.
    """
    ticket = models.ForeignKey(Ticket)
    date_sent = models.DateTimeField(auto_now_add=True)
    email = PickleField()

    class Meta:
        verbose_name = u"Logs des mails envoyés"
        verbose_name_plural = u"Logs des mails envoyés"
        ordering = ["date_sent"]

class TicketAlarmManager(models.Manager):
    def get_query_set(self):
        qs = super(TicketAlarmManager, self).get_query_set().\
                select_related('user_open')
        return qs

class TicketAlarmOpenManager(TicketAlarmManager):
    def get_query_set(self):
        qs =  super(TicketAlarmOpenManager, self).get_query_set().\
                select_related('ticket__title').\
                filter(user_close__isnull=True)
        return qs

class TicketAlarm(models.Model):

    objects = TicketAlarmManager()
    opened = TicketAlarmOpenManager()

    reason = models.CharField(u"Raison", max_length=128)
    date_open = models.DateTimeField(u"Date de creation", auto_now_add = True)
    user_open = models.ForeignKey(User, related_name="ticket_alarm_open")
    date_close = models.DateTimeField(u"Date de fermeture", null=True )
    user_close = models.ForeignKey(User, related_name="ticket_alarm_close", null=True)
    ticket = models.ForeignKey(Ticket)

    def title_string(self):
        if self.id:
            ret = "Alarme ouverte le %s par %s" % (self.date_open.strftime('%d/%m/%Y à %H:%M'), self.user_open,)
        else:
            ret = "Nouvelle alarme"
        return ret

    def __unicode__(self):
        return self.reason

class TicketAppelManager(models.Manager):
    def get_query_set(self):
        return super(TicketAppelManager, self).get_query_set().\
                select_related('user')

class TicketAppel(models.Model):
    """ Liste de date où le client a rappelé  """
    class Meta:
        ordering = ["date"]

    objects = TicketAppelManager()

    date = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)

    def save(self, **kwargs):
        ticket = Ticket.minimal.get(pk=self.ticket.pk)
        # peut être mieux de recalculer à chaque fois ....
        ticket.nb_appels = models.F('nb_appels') + 1
        ticket.save()
        super(TicketAppel, self).save()

#moderator.register(Ticket, TicketCommentModerator)

# Update last_modification time
comment_was_posted.connect(Ticket.handle_comment_posted_signal)

# Google calendar sync
models.signals.pre_save.connect(Ticket.handle_ticket_presave_signal, sender=Ticket)
