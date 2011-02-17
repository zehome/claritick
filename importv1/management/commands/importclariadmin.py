# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment

import datetime
import psycopg2
import traceback
import imp

import claritick.clariadmin.models as amod
import claritick.common.models as cmod


class Command(BaseCommand):
    args = "<config_file>"
    
    @staticmethod
    def _clariadmin_select(db, query, **args):
        cursor = db.cursor()
        cursor.execute(query, **args)
        return cursor.fetchall()
    
    def handle(self, *args, **options):
        print "importing clariadmin hosts from clariadmin"
        
        print "Args: %s" % (args,)
        if not args:
            print u"Utilisation: %s importclariadmin fichierdeconfig.py"
            return
        
        try:
            config = imp.load_source("clariadmin_config", args[0])
        except:
            print "Erreur d'importation."
            raise
        
        print dir(config)
        # Verification des paramètres
        try:
            pre_mapping_sites = config.clariadmin_claritick_site_mapping
            pre_mapping_marque = config.clariadmin_claritick_marque_mapping
            dsnmap = config.dsnmap
        except AttributeError:
            print "Le module de configuration ne dispose pas des attributs necessaires."
            raise
        
        print "Connecting to database dsnmap: %s" % (dsnmap,)
        try:
            db = psycopg2.connect(**dsnmap)
        except:
            print "Bah il m'aime pas : %s" % (traceback.format_exc(),)
            return
        
        clariadmin_claritick_site_mapping = {}
        
        print "Verification association site clariadmin/claritick"
        rows = self._clariadmin_select(db, "SELECT id_site,libelle,site FROM clariadmin_site join clariadmin_groupe using (id_groupe) ORDER BY id_groupe, site")
        for row in rows:
            try:
                mapping_row = pre_mapping_sites[int(row[0])]
            except KeyError:
                print "[FAIL]: Site %s on groupe %s id=%s not found in mapping." % (row[2], row[1], row[0])
            else:
                # Getting claritick site
                try:
                    site = cmod.Client.objects.get(pk=mapping_row)
                except cmod.Client.DoesNotExist:
                    print "[FAIL]: Client id=%s not found in claritick! (refering to clariadmin: Site %s groupe=%s id=%s)" % (mapping_row, row[2], row[1], row[0])
                else:
                    print "[OK]: %s - %s => %s" % (row[1], row[2], site)
                    clariadmin_claritick_site_mapping[int(row[0])] = site
        
        print "Mapping/Génération HostType..."
        clariadmin_claritick_hosttype_mapping = {}
        rows = self._clariadmin_select(db, "SELECT gateway, description, id_type FROM clariadmin_hosttype ORDER BY id_type")
        for row in rows:
            try:
                hosttype = amod.HostType.objects.get(text=row[1], gateway=row[0])
            except amod.HostType.DoesNotExist:
                hosttype = amod.HostType(text=row[1], gateway=row[0])
                hosttype.save()            
            clariadmin_claritick_hosttype_mapping[row[2]] = hosttype
        
        print "Mapping/Génération OS..."
        clariadmin_claritick_operatingsystem_mapping = {}
        rows = self._clariadmin_select(db, "SELECT osname, version, id_os FROM clariadmin_os ORDER BY id_os")
        for row in rows:
            try:
                os = amod.OperatingSystem.objects.get(name=row[0], version=row[1])
            except amod.OperatingSystem.DoesNotExist:
                os = amod.OperatingSystem(name=row[0], version=row[1])
                os.save()            
            clariadmin_claritick_operatingsystem_mapping[row[2]] = os
        
        print "Mapping/Génération Marque/Modèle..."
        clariadmin_claritick_marque_mapping = {}
        rows = self._clariadmin_select(db, "SELECT libelle, id_marque FROM clariadmin_marque ORDER BY id_marque")
        for row in rows:
            # On essaye de trouver un mapping dans le premap
            try:
                premap = pre_mapping_marque[row[1]]
            except KeyError:
                premap = None
            supplier = None
            if premap:
                try:
                    supplier = amod.Supplier.objects.get(name=premap)
                except amod.Supplier.DoesNotExist:
                    supplier = amod.Supplier(name=premap)
            if not supplier:
                supplier = amod.Supplier(name=row[0])
                supplier.save()
            
            clariadmin_claritick_marque_mapping[row[1]] = supplier
        #~ return
        print "Migration Host..."
        rows = self._clariadmin_select(db, """SELECT site, hosttype, os, 
            id_marque, hostname, rootpw, 
            commentaire, ip, date_ajout, 
            modele, emplacement, numero_serie, 
            date_en_service, date_fin_garantie, statut, automate FROM clariadmin_host ORDER BY site, id_host""")
        
        for row in rows:
            # On le cherche voir si on a déja
            try:
                host = amod.Host.objects.get(hostname=row[4], ip=row[7])
            except amod.Host.DoesNotExist:
                # Ok, import
                try:
                    host = amod.Host()
                    try:
                        host.site = clariadmin_claritick_site_mapping[row[0]]
                    except:
                        print "[FAIL]: Le site id_clariadmin=%s n'est pas présent dans le mapping claritick." % (row[0],)
                        continue
                    host.type = clariadmin_claritick_hosttype_mapping[row[1]]
                    host.os = clariadmin_claritick_operatingsystem_mapping[row[2]]
                    host.supplier = clariadmin_claritick_marque_mapping[row[3]]
                    host.hostname = row[4]
                    host.rootpw = row[5]
                    host.commentaire = row[6]
                    host.ip = row[7]
                    if row[8]:
                        host.date_add = row[8]
                    try:
                        premap_marque = pre_mapping_marque[row[3]]
                        if premap_marque:
                            host.model = premap_marque
                    except KeyError:
                        pass
                    host.model = row[9]
                    host.location = row[10]
                    host.serial = row[11]
                    if row[12]:
                        host.date_start_prod = row[12]
                    if row[13]:
                        host.date_end_prod = row[13]
                    if row[14] == 1:
                        host.status = "HS"
                    if row[15]:
                        host.commentaire += "AUTOMATE:%s\n" % (row[15],)
                    host.save()
                    print "[OK]: %s" % (host,)
                except:
                    print "[FAIL]: Unknown error %s" % (traceback.format_exc(),)
                    continue
                
            else:
                print "[FAIL] Host %s déja présent." % (host,)
            