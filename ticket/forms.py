# -*- coding: utf-8 -*-

from django import forms

from claritick.ticket.models import *
from claritick.ticket.models import Client
from claritick.common.widgets import *
from dojango import forms as df

class TelephoneField(forms.Field):
    def clean(self, value):
        if not value:
            return
        
        try:
            cleaned_value = value.replace(" ", "").replace(".", "")
        except:
            raise ValidationError("Numero de telephone invalide.")
        
        if len(cleaned_value) != 10:
            raise forms.ValidationError("Le numero de telephone doit comporter 10 chiffres.")

        return cleaned_value

class PartialNewTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("category",)

class NewTicketForm(df.ModelForm):
    title = df.CharField(widget=df.TextInput(attrs={'size':'64'}))
    text = df.CharField(widget=df.Textarea(attrs={'cols':'90', 'rows': '20'}))
    
    client = df.ModelChoiceField(queryset = Client.objects.all(),
       widget=df.FilteringSelect(attrs={'queryExpr': '*${0}*'}), empty_label='')
    class Meta:
        model = Ticket
        exclude = ("opened_by",)