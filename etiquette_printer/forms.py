# -*- coding: utf-8 -*-

import traceback

from django.template import Context, Template
from django import db

import dojango.forms as df

from common.forms import MyDojoFilteringSelect

from etiquette_printer.models import EtiquetteTemplate
from etiquette_printer.unaccent import purify

class PermissionDenied(Exception):
    pass

class PrintOrderForm(df.Form):
    template = df.ModelChoiceField(queryset=EtiquetteTemplate.objects.all(),
            widget=MyDojoFilteringSelect(), label=u'Template')
    nombre_etiquettes = df.IntegerField(label=u'Nombre d\'étiquettes', initial=1)
    
    def get_output(self, pk, user):
        assert(self.is_valid())
        try:
            model = db.models.get_model(self.cleaned_data['template'].app_name, self.cleaned_data['template'].model_name)
        except:
            raise PermissionDenied
        
        # LC: Uggly.
        print pk
        try:
            instance = model.objects.filter(pk=pk).filter_ticket_by_user(user)[0]
        except IndexError:
            raise PermissionDenied("No ticket orresponding.")
        except:
            raise PermissionDenied
        
        tmplt = Template(self.cleaned_data['template'].template)
        context_dict = {
            'instance': instance,
            'nombre_etiquettes': self.cleaned_data["nombre_etiquettes"],
            'printer_ip': self.cleaned_data['template'].printer_ip,
        }
        ctx = Context(context_dict)
        output_data = tmplt.render(ctx)
        # Replace accents...
        x = purify(output_data)
        print x
        return x

