# -*- coding: utf-8 -*-

from django import forms
from dojango import forms as df

from django.contrib.auth.models import User
from claritick.ticket.models import *
from claritick.common.widgets import *
from claritick.common.forms import ModelFormTableMixin

class PartialNewTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("category",)

class NewTicketForm(df.ModelForm):
    title = df.CharField(widget=df.TextInput(attrs={'size':'64'}))
    text = df.CharField(widget=df.Textarea(attrs={'cols':'90', 'rows': '20'}))
    
    client = df.ModelChoiceField(queryset = Client.objects.all(),
       widget=df.FilteringSelect(attrs={'queryExpr': '${0}*'}), empty_label='')
    class Meta:
        model = Ticket
        exclude = ("opened_by",)

class SearchTicketForm(df.ModelForm, ModelFormTableMixin):
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
    
    class Meta:
        fields = ('category', 'project', 'priority', 'state',
                  'client', 'contact', 'opened_by', 'assigned_to', 
                  'title', 'text', 'keywords')
        model = Ticket
