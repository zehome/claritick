# -*- coding: utf-8 -*-
from django.db import models
import re
from clariadmin.models import Host

ACTIONS_LOG = [
    (0, u"consulté", "#FFFFFF"),
    (1, u"créé", "#77FF77"),
    (2, u"modifié", "#FFFF77"),
    (3, u"supprimé", "#FF7777")]

class HostEditLog(models.Model):
    class Meta:
        ordering = ('date',)
    host = models.ForeignKey(Host, verbose_name=u"Machine", blank=True, null=True, on_delete=models.SET_NULL)
    #user = models.ForeignKey(User, verbose_name=u"Utilisateur", blank=True, null=True, on_delete=models.SET_NULL)
    username = models.CharField("Nom utilisateur", max_length=128)
    date = models.DateTimeField(u"Date d'ajout", auto_now_add=True)
    ip = models.CharField(u'Ip utilisateur', max_length=1024)
    action = models.IntegerField(u"Action" ,choices=((i,s) for i,s,c in ACTIONS_LOG))
    message = models.CharField(u'Action répertoriée', max_length=1024)

    @property
    def color(self):
        return dict((i,c) for i,s,c in ACTIONS_LOG)[self.action]

    @property
    def action_text(self):
        return dict((i,s) for i,s,c in ACTIONS_LOG)[self.action]

    message_format = u"Le poste %s a été %s par %s (sec:%s, ip:%s) le %s"

    def parse_message(self):
        infos = re.match(ur"Le poste ([\w\W]+) a été ([\wé]+) par (\w+) " +
                  ur"\(sec:(\d+), ip:(\d?\d?\d.\d?\d?\d.\d?\d?\d.\d?\d?\d)\)" +
                  ur" le (\d?\d/\d?\d/\d?\d?\d\d \d?\d:\d?\d)\Z",self.message)
        if infos:
            return infos
        else:
            raise Exception('invalid message')

    def __init__(self,*args,**kwargs):
        action = kwargs.pop("action",None)
        if isinstance(action, unicode):
            action = dict((s,i) for i,s,c in ACTIONS_LOG)[action]
        super(HostEditLog,self).__init__(*args, action=action, **kwargs)

class HostVersion(models.Model):
    class Meta:
        ordering = ("log_entry__date",)
    host = models.TextField(u"Host data")
    additionnal_fields = models.TextField(u"Host additionnal fields", null=True)
    log_entry = models.OneToOneField(HostEditLog)

# Create your models here.
