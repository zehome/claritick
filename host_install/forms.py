#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dojango.forms as df
from host_install.models import InstallationOrder
import random

attrs_filtering={'queryExpr':'*${0}*','highlightMatch':'all','ignoreCase':'true','autoComplete':'false'}

class InstallationOrderForm(df.ModelForm):
    class Meta:
        model=InstallationOrder
        fields=("serial", "hostname","site","fai_classes","ip","netmask","gateway",
                "dns1","dns2","ip_mca","ip_clarilab","supplier","inventory",
                "location","commentaire",)
                #"rootpw",
        widgets={'site':df.FilteringSelect(attrs_filtering),
                 'supplier':df.FilteringSelect(attrs_filtering),
                 'ip':df.IPAddressTextInput(),
                 'gateway':df.IPAddressTextInput(),
                 'dns1':df.IPAddressTextInput(),
                 'dns2':df.IPAddressTextInput(),
                 'ip_mca':df.IPAddressTextInput(),
                 'ip_clarilab':df.IPAddressTextInput(),
                 'netmask':df.IPAddressTextInput(),
                }
    def __init__(self, *args, **kwargs):
        super(df.ModelForm,InstallationOrderForm).__init__(self,*args,**kwargs)
        if(not self.instance.pk):
            #TODO:CN -> générer un mot de passe clarisys compliant
            self.instance.rootpw=''.join([chr(random.randint(65,122)) for i in
                                          range(10)])

# vim:set et sts=4 ts=4 tw=80:
