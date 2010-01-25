# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment

import datetime
import _mysql
import traceback

import claritick.ticket.models as tmod
import claritick.common.models as cmod

def recoder(string):
    if string is None:
        return string
    return string.decode('ISO-8859-15').encode('UTF-8')

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        print "importing tickets from v1"
        print "tentative de connexion à la base drupal"
        try:
            db = _mysql.connect("192.168.1.2","drupal","Ex9phaph","drupal")
        except:
            print "Bah il m'aime pas : %s" % (traceback.format_exc(),)
        else:
            print "Ok, cool..."
            print "Creation des etats"
            for etat_data in [(1,'Nouveau',0),(2,'Actif',1),(3,'En attente',2),(4,'Fermé',3)]:
                etat = tmod.State(id = etat_data[0], label = etat_data[1], weight = etat_data[2])
                etat.save()
            print "Done"
            
            print "Creation des utilisateurs"
            db.query("SELECT name FROM users where name is not null and name != ''")
            r = db.store_result()
            for username in r.fetch_row(maxrows = 0):
                if User.objects.filter(username = username[0]).count() == 0:
                    User.objects.create_user(username[0],'',username[0])
            print "Done"
            
            print "Creation des priorites"
            db.query("SELECT * from support_priority")
            r = db.store_result()
            for prio_data in r.fetch_row(maxrows = 0):
                prio = tmod.Priority(id = prio_data[0], label = prio_data[1], warning_duration = prio_data[3])
                prio.save()
            print "Done"
            
            print "Creation des projets"
            db.query("SELECT * from support_client")
            r = db.store_result()
            for pro_data in r.fetch_row(maxrows = 0):
                pro = tmod.Project(id = pro_data[0], label = recoder(pro_data[1]))
                pro.save()
            print "Done"
            
            print "Creation des clients"
            db.query("select term_data.tid,term_data.name,term_hierarchy.parent,group_concat(distinct content_field_client_mail.field_client_mail_value separator ',') from term_data, term_hierarchy,taxonomynode, content_field_client_mail where term_data.vid = 2 and term_data.tid = term_hierarchy.tid and term_data.tid = taxonomynode.tid and content_field_client_mail.nid = taxonomynode.nid group by taxonomynode.nid")
            r = db.store_result()
            rows = r.fetch_row(maxrows = 0)
            for cl_data in rows:
                parent = None
                cl = cmod.Client(id = cl_data[0], label = recoder(cl_data[1]), parent = parent, emails = cl_data[3])
                cl.save()
            for cl_data in rows:
                if cl_data[2] != '0':
                    cl = cmod.Client.objects.get(pk = cl_data[0])
                    parent = cmod.Client.objects.get(pk = cl_data[2])
                    cl.parent = parent
                    cl.save()
            print "Done"
            
            print "Creation des Categories"
            for cat in tmod.Category.objects.all():
                cat.delete()
            db.query("select distinct(field_ticket_type_value) from content_type_support_ticket where field_ticket_type_value is not null")
            r = db.store_result()
            for cat_data in r.fetch_row(maxrows = 0):
                cat = tmod.Category(label = recoder(cat_data[0]))
                cat.save()
            defcat = tmod.Category(label = 'Ticket')
            defcat.save()
            print "Done"
            
            print "Creation des tickets"
            ticket_content_type = ContentType.objects.get_for_model(tmod.Ticket)
            db.query("""select
                st.nid as id,
                ctst.field_ticket_contact_value as contact,
                ctst.field_ticket_phone_value as telephone,
                node.created as date_open,
                st.state as state,
                st.priority as priority,
                assusr.name as assigned_to,
                creusr.name as opened_by,
                nr.title as title,
                nr.body as text,
                ctst.field_ticket_type_value as category_label
                
                from support_ticket as st join node on (node.nid = st.nid) join users as assusr on (st.assigned = assusr.uid) join users as creusr on (node.uid = creusr.uid) join content_type_support_ticket as ctst on (node.nid = ctst.nid and node.vid = ctst.vid) join node_revisions as nr on (nr.nid = node.nid and node.vid = nr.vid) order by id""")
            r = db.store_result()
            rows = r.fetch_row(maxrows = 0)
            print "%s tickets a creer" % (len(rows),)
            cpt = 0
            for tic_data in rows:
                cpt += 1
                try:
                    category = tmod.Category.objects.get(label = recoder(tic_data[10]))
                except tmod.Category.DoesNotExist:
                    category = tmod.Category.objects.get(label = 'Ticket')
                try:
                    assigned_to = User.objects.get(username = tic_data[6])
                except User.DoesNotExist:
                    assigned_to = None
                try:
                    opened_by = User.objects.get(username = tic_data[7])
                except User.DoesNotExist:
                    opened_by = None
                tic = tmod.Ticket(
                    id = tic_data[0],
                    contact = tic_data[1] and recoder(tic_data[1]) or '',
                    telephone = tic_data[2] and tic_data[2] or '',
                    date_open = datetime.datetime.fromtimestamp(int(tic_data[3])),
                    state = tmod.State.objects.get(pk = int(tic_data[4])),
                    priority = tmod.Priority.objects.get(pk = int(tic_data[5])),
                    assigned_to = assigned_to,
                    opened_by = opened_by,
                    title = recoder(tic_data[8]),
                    text = recoder(tic_data[9]),
                    category = category,
                    )
                tic.save()
            print "Done"
            
            print "Creation des reponses"
            db.query("select comments.nid, users.name, comments.comment, comments.timestamp from comments join users on (comments.uid = users.uid)")
            r = db.store_result()
            rows = r.fetch_row(maxrows = 0)
            cpt =0
            for c_data in rows:
                cpt += 1
                if recoder(c_data[2]):
                    try:
                        ticket = tmod.Ticket.objects.get(pk = int(c_data[0]))
                    except tmod.Ticket.DoesNotExist:
                        print "pas de ticket %s" % (c_data[0],)
                        pass
                    else:
                        try:
                            user = User.objects.get(username = c_data[1])
                        except User.DoesNotExist:
                            user = None
                        c = Comment(site_id = 1, content_object = ticket, content_type = ticket_content_type, comment = recoder(c_data[2]), user = user, user_name = user.username, submit_date = datetime.datetime.fromtimestamp(int(c_data[3])))
                        c.save()
            print "Done"
            
            print "Affectation clients/tickets"
            for ticket in tmod.Ticket.objects.all():
                db.query("select distinct th.tid,th.parent from term_node as tn join term_hierarchy as th on (th.tid = tn.tid) join term_data as td on (td.tid = tn.tid) where tn.nid = %s and td.vid = 2" % (ticket.pk,))
                r = db.store_result()
                clients = r.fetch_row(maxrows = 0)
                if len(clients) == 0:
                    print "rien pour %s" % (ticket.pk,)
                    continue
                elif len(clients) == 1:
                    id_client = int(clients[0][0])
                elif len(clients) == 2:
                    if clients[0][0] == clients[1][1]:
                        id_client = int(clients[1][0])
                    elif clients[1][0] == clients[0][1]:
                        id_client = int(clients[0][1])
                    else:
                        print "OOOOOOOOOOAAAAAAAh %s sur le ticket %s" % (clients, ticket.pk,)
                else:
                    print "BEeeeeeeeurk %s sur le ticket %s" % (clients, ticket.pk,)
                if id_client:
                    try:
                        ticket.client = cmod.Client.objects.get(pk = id_client)
                        ticket.save()
                    except cmod.Client.DoesNotExist:
                        print "SNnniifff client %s existe pas sur ticket %s" % (id_client, ticket.pk,)
                else:
                    print "Putaaaain ! pas d'id client sur le ticket %s" % (ticket.pk,)
            print "Done"
            
            #~ print "Recuperation des donnees"
            #~ db.query("""SELECT * from support_ticket""")
            #~ r = db.store_result()
            #~ rows = r.fetch_row(maxrows = 0)
            #~ for row in rows:
                #~ print row