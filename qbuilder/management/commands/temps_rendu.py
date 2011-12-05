#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from optparse import make_option
import logging
import time
import datetime
import traceback
from tat.models import MemorisationTempsRendu, ModeleEvenement
logger = logging.getLogger("qbuilder.temps_rendu")

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("--start",
            dest="start_date_string",
            help=u"Calculer les temps de rendu à partir de cette date (YYYY-mm-dd)",
            ),
        make_option("--end",
            dest="end_date_string",
            help=u"Calculer les temps de rendu jusqu'à cette date (YYYY-mm-dd)",
            ),
        )

    def handle(self, *args, **kwargs):
        allowed_hour = getattr(settings, 'QB_TEMPS_RENDU_HOUR', 1)
        actual_hour = datetime.datetime.now().hour
        if actual_hour != allowed_hour:
            logger.warning(u"Only allowed to run at %s and it is %s", allowed_hour, actual_hour)
            return
        start_date = datetime.date.today() - datetime.timedelta(days = 1)
        end_date = datetime.date.today()
        start_date_string = kwargs.pop('start_date_string')
        end_date_string = kwargs.pop('end_date_string')
        if start_date_string:
            start_date = datetime.datetime.strptime(start_date_string,'%Y-%m-%d')
        if end_date_string:
            end_date = datetime.datetime.strptime(end_date_string,'%Y-%m-%d')
        SQL = """
            SELECT
                series.date,
                mca3.vstats_tat.start_evt,
                mca3.vstats_tat.end_evt,
                mca3.vstats_tat.start,
                mca3.vstats_tat."end",
                AVG(mca3.vstats_tat.temps_reel),
                MIN(mca3.vstats_tat.temps_reel),
                MAX(mca3.vstats_tat.temps_reel),
                COUNT(mca3.vstats_tat.temps_reel)
            FROM mca3.vstats_tat,
                 (select start, "end" from mca3.delai) as const,
                 (select generate_series(%s, %s, '1 day'::interval) as date) as series
            WHERE mca3.vstats_tat.end_date > series.date AND
                  mca3.vstats_tat.end_date < series.date + '1 day'::interval AND
                  mca3.vstats_tat.start = const.start AND
                  mca3.vstats_tat."end" = const."end" AND
                  mca3.vstats_tat.temps_reel > '0'::interval AND
                  mca3.vstats_tat.start != mca3.vstats_tat."end"
            GROUP BY series.date,
                     mca3.vstats_tat.start_evt,
                     mca3.vstats_tat.end_evt,
                     mca3.vstats_tat.start,
                     mca3.vstats_tat."end"
        """
        logger.info("Calcul des temps de rendu (%s - %s)", start_date, end_date,)
        modeles = ModeleEvenement.objects.all()
        modeles = dict([(modele.pk, modele) for modele in modeles])
        now = time.time()
        cursor = connection.cursor()
        try:
            cursor.execute(SQL, [start_date, end_date,])
        except:
            logger.error("Erreur d'exécution : %s" % (traceback.format_exc(),))
        else:
            logger.info("Temps d'exécution : %s" % (time.time() - now,))
            for dataline in cursor.fetchall():
                stev = modeles[dataline[3]]
                edev = modeles[dataline[4]]
                MemorisationTempsRendu.objects.create(
                    date = dataline[0],
                    start_evt = stev.evenement,
                    end_evt = edev.evenement,
                    start = stev,
                    end = edev,
                    avg_temps_rendu = dataline[5],
                    min_temps_rendu = dataline[6],
                    max_temps_rendu = dataline[7],
                    compte = dataline[8]
                    )
