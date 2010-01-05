# -*- coding: utf-8 -*-

from django import forms
from claritick.ticket.models import *

import re

datetime_formats = ('%d/%m/%Y %H:%M:%S', )
date_formats = ('%Y-%m-%d', )

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

class NewTicketForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size':'64'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'cols':'90', 'rows': '20'}))
    keywords = forms.CharField(widget=forms.TextInput(attrs={'size': 32}))
    class Meta:
        model = Ticket
        exclude = ("opened_by",)