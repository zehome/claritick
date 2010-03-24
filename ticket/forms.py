# -*- coding: utf-8 -*-

from django import forms
from dojango import forms as df

from django.contrib.auth.models import User
from claritick.ticket.models import *
from claritick.common.widgets import *
from claritick.common.forms import ModelFormTableMixin
from claritick.common.models import UserProfile

def filter_form_for_user(form, user):
    if user.is_superuser:
        form.base_fields["client"].choices = [(x.pk, x) for x in Client.objects.all()]
    else:
        try:
            form.base_fields["client"].choices = [(x.pk, x) for x in user.get_profile().get_clients()]
        except UserProfile.DoesNotExist:
            # TODO Pas de profil, on affiche tous les clients ? Aucuns ?
            form.base_fields["client"].choices = []
    form.base_fields["client"].choices.insert(0, ("", ""))

class PartialNewTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("category",)

class NewTicketForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}))
    text = df.CharField(widget=df.Textarea(attrs={'cols':'90', 'rows': '20'}))
    client = df.ModelChoiceField(queryset = Client.objects.all(),
         widget=df.FilteringSelect(attrs={'queryExpr': '${0}*'}), empty_label='', required=False)
    keywords = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}), required=False)

    calendar_start_time = df.DateTimeField(required=False)
    calendar_end_time = df.DateTimeField(required=False)
    
    class Meta:
        model = Ticket
        exclude = ("opened_by",)

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            filter_form_for_user(self, kwargs["user"])
            del kwargs["user"] # user= ne doit pas arriver a l'init parent ...
        super(NewTicketForm, self).__init__(*args, **kwargs)

class SearchTicketForm(df.Form, ModelFormTableMixin):
    title = df.CharField(widget=df.TextInput(attrs={'size':'64'}), required=False)
    client = df.ModelChoiceField(queryset = Client.objects.all(),
        widget=df.FilteringSelect(attrs={'queryExpr': '${0}*'}), empty_label='', required=False)
    category = df.ModelChoiceField(queryset = Category.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    project = df.ModelChoiceField(queryset = Project.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    state = df.ModelChoiceField(queryset = State.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    priority = df.ModelChoiceField(queryset = Priority.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    assigned_to = df.ModelChoiceField(queryset = User.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    
    text = df.CharField(required=False)
    opened_by = df.ModelChoiceField(queryset = User.objects.all(), 
        widget=df.FilteringSelect(), required=False)
    keywords = df.CharField(required=False)
    contact = df.CharField(required=False)

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            filter_form_for_user(self, kwargs["user"])
            del kwargs["user"] # user= ne doit pas arriver a l'init parent ...
        super(SearchTicketForm, self).__init__(*args, **kwargs)
