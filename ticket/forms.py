# -*- coding: utf-8 -*-

import datetime
from django import forms
from dojango import forms as df
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site

from claritick.ticket.models import *
from claritick.common.widgets import *
from claritick.common.forms import ModelFormTableMixin
from claritick.common.models import UserProfile

from common.exceptions import NoProfileException
from common.models import UserProfile, ClaritickUser
from common.utils import filter_form_for_user

class PartialNewTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("category",)

class NewTicketForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}))
    text = df.CharField(widget=forms.Textarea(attrs={'cols':'90', 'rows': '20'}))
    client = df.ModelChoiceField(queryset = Client.objects.all(),
         widget=df.FilteringSelect(attrs={'queryExpr': '${0}*'}), empty_label='', required=False)
    keywords = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}), required=False)
    calendar_start_time = df.DateTimeField(required=False)
    calendar_end_time = df.DateTimeField(required=False)
    assigned_to = df.ModelChoiceField(widget=df.FilteringSelect(), queryset=ClaritickUser.objects_with_clients.all())
    validated_by = df.ModelChoiceField(widget=df.FilteringSelect(), queryset=ClaritickUser.objects_with_clients.all())
    
    class Meta:
        model = Ticket
        exclude = ("opened_by",)

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            filter_form_for_user(self, kwargs["user"])
            del kwargs["user"] # user= ne doit pas arriver a l'init parent ...
        super(NewTicketForm, self).__init__(*args, **kwargs)

class NewTicketSmallForm(NewTicketForm):

    class Meta:
        model = Ticket
        exclude = ("opened_by", "category", "project", "keywords", "state", "priority")

class SearchTicketForm(df.Form, ModelFormTableMixin):
    title       = df.CharField(widget=df.TextInput(attrs={'size':'64'}), required=False)
    client      = df.ChoiceField(choices=[(x.pk, x) for x in Client.objects.all()],
        widget=df.FilteringSelect(attrs={'queryExpr': '${0}*'}), required=False)
    category    = df.ModelChoiceField(queryset = Category.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    project     = df.ModelChoiceField(queryset = Project.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    state       = df.ModelChoiceField(queryset = State.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    priority    = df.ModelChoiceField(queryset = Priority.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    assigned_to = df.ChoiceField(widget=df.FilteringSelect(), required=False)
    
    text = df.CharField(required=False)
    opened_by = df.ChoiceField(widget=df.FilteringSelect(), required=False)
    keywords = df.CharField(required=False)
    contact = df.CharField(required=False)

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            filter_form_for_user(self, kwargs["user"])
            del kwargs["user"] # user= ne doit pas arriver a l'init parent ...
        self.base_fields["assigned_to"].choices = [(x.pk, x) for x in ClaritickUser.objects_with_clients.all()]
        self.base_fields["assigned_to"].choices.insert(0, ("", ""))
        self.base_fields["opened_by"].choices = self.base_fields["assigned_to"].choices
        super(SearchTicketForm, self).__init__(*args, **kwargs)

class SearchTicketViewForm(SearchTicketForm):
    client      = df.ChoiceField(choices=[(x.pk, x) for x in Client.objects.all()],
        widget=df.FilteringSelect(attrs={'queryExpr': '${0}*'}), required=False)
    view_name = forms.CharField(widget=df.TextInput(), label="Nom de la vue", required=False)
    state       = forms.MultipleChoiceField(choices=State.objects.values_list("pk", "label"), required=False, widget=df.CheckboxSelectMultiple())
    category = forms.MultipleChoiceField(choices=Category.objects.values_list("pk", "label"), required=False, widget=df.CheckboxSelectMultiple())
    project  = forms.MultipleChoiceField(choices=Project.objects.values_list("pk", "label"), required=False, widget=df.CheckboxSelectMultiple())
    priority = forms.MultipleChoiceField(choices=Priority.objects.values_list("pk", "label"), required=False, widget=df.CheckboxSelectMultiple())
    assigned_to = forms.MultipleChoiceField(required=False, widget=df.CheckboxSelectMultiple())
    opened_by   = forms.MultipleChoiceField(required=False, widget=df.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super(SearchTicketViewForm, self).__init__(*args, **kwargs)

        # On retire les choix vide, provenant de SearchTicketForm
        del self.base_fields["assigned_to"].choices[0]
        del self.base_fields["opened_by"].choices[0]

    def clean_view_name(self):
        name = self.cleaned_data["view_name"]
        if name == "" or name is None:
            return u"Nouvelle vue"
        return name

class TicketActionsForm(df.Form):
    actions     = df.ChoiceField(widget=df.FilteringSelect(), required=False)
    assigned_to = df.ModelChoiceField(queryset=User.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    category    = df.ModelChoiceField(queryset = Category.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    project     = df.ModelChoiceField(queryset = Project.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    state       = df.ModelChoiceField(queryset = State.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    priority    = df.ModelChoiceField(queryset = Priority.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    comment     = df.CharField(widget=df.HiddenInput(), required=False)

    model = Ticket.objects

    def __init__(self, *args, **kwargs):
        try:
            self.queryset = self.model.filter(id__in=args[0].getlist("ticket_checked"))
        except KeyError:
            self.queryset = self.model.none()

        self.base_fields["actions"].choices = self.get_actions()
        self.base_fields["actions"].choices.insert(0, ("", ""))
        self.base_fields["assigned_to"].choices = [(x.pk, x) for x in ClaritickUser.objects_with_clients.all()]
        self.base_fields["assigned_to"].choices.insert(0, ("", ""))
        super(TicketActionsForm, self).__init__(*args, **kwargs)

    def get_actions(self):
        return [
            ("action_close_tickets", u"Fermer les tickets sélectionnés"),
            ("action_change_assigned_to", u"Modifier l'assignation"),
            ("action_change_category", u"Modifier la catégorie"),
            ("action_change_project", u"Modifier le projet"),
            ("action_change_state", u"Modifier l'état"),
            ("action_change_priority", u"Modifier la priorité"),
            ("action_validate_tickets", u"Valider les tickets sélectionnées"),
        ]

    def process_actions(self, request):
        if self.is_valid():
            action = self.cleaned_data["actions"]
            try:
                attr = getattr(self, action)
                attr(self.queryset, request)
                return True
            except AttributeError:
                return False
        return False

    def clean(self):
        cd = self.cleaned_data
        if cd["actions"] == "action_close_tickets" or (
            cd["actions"] == "action_change_state" and cd["state"] and cd["state"].pk == settings.TICKET_STATE_CLOSED):
            if not cd["comment"]:
                raise forms.ValidationError(u"Vous devez saisir un commentaire de clotûre pour le/les tickets sélectionné(s).")

        if cd["actions"] == "action_change_state" and not cd["state"]:
            raise forms.ValidationError(u"Vous devez choisir un état à appliquer.")
        if cd["actions"] == "action_change_assigned_to" and not cd["assigned_to"]:
            raise forms.ValidationError(u"Vous devez choisir une nouvelle assignation.")
        if cd["actions"] == "action_change_category" and not cd["category"]:
            raise forms.ValidationError(u"Vous devez choisir une nouvelle catégorie.")
        if cd["actions"] == "action_change_project" and not cd["project"]:
            raise forms.ValidationError(u"Vous devez choisir un nouveau project.")
        if cd["actions"] == "action_change_priority" and not cd["priority"]:
            raise forms.ValidationError(u"Vous devez choisir une nouvelle priorité.")
 
        return cd

    def action_close_tickets(self, qs, request):
        qs.update(state=settings.TICKET_STATE_CLOSED, date_close=datetime.datetime.now())
        for ticket in qs:
            Comment.objects.create(
                content_object=ticket,
                site=Site.objects.get_current(),
                user=request.user,
                user_name=request.user.username,
                user_email=request.user.email,
                comment=self.cleaned_data["comment"],
                submit_date=datetime.datetime.now(),
                is_public=True,
                is_removed=False
            )

    def action_change_assigned_to(self, qs, request):
        qs.update(assigned_to=self.cleaned_data["assigned_to"])

    def action_change_category(self, qs, request):
        qs.update(category=self.cleaned_data["category"])

    def action_change_project(self, qs, request):
        qs.update(project=self.cleaned_data["project"])

    def action_change_state(self, qs, request):
        if self.cleaned_data["state"].pk == settings.TICKET_STATE_CLOSED:
            self.action_close_tickets(qs, request)
        else:
            qs.update(state=self.cleaned_data["state"])

    def action_change_priority(self, qs, request):
        qs.update(priority=self.cleaned_data["priority"])
    
    def action_validate_tickets(self, qs, request):
        qs.update(validated_by=request.user)

class TicketActionsSmallForm(TicketActionsForm):

    def get_actions(self):
        return [
            ("action_close_tickets", u"Fermer les tickets sélectionnés"),
        ]

    def process_actions_(self):
        if self.is_valid():
            if self.cleaned_data["actions"] not in ("action_close_tickets"):
                return False
            return super(TicketActionsSmallForm, self).process_actions()
