#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from gui.models import ParametrageCompteur, CompteurCustom
from testmca.models import automate
from psycopg2 import ProgrammingError
from psycopg2.extras import DictCursor
import time, logging, datetime
logger = logging.getLogger("qbuilder.queryrunner")

from qbuilder.models import QueryParameters, QueryResult
from qbuilder.views import make_db_url
from qbuilder.lib import jsondump
from qbuilder.main import QBuilder
from django.utils import simplejson as json
from django.conf import settings
from gui.utils import serializable_list
import traceback

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for qu in QueryParameters.objects.all():
            try:
                jsondata = json.loads(qu.data)
            except ValueError:
                # Incorrect JSON, ignore this query
                logger.error("Incorrect JSON data in query [%s]", qu)
                continue
            if qu.status > 0: # Don't restart queries in error
                running_delay = datetime.timedelta(seconds = int(jsondata.get("running_delay", 15*60))) # Default : 15 minutes
                last_launch = QueryResult.objects.filter(query = qu).order_by("-date")
                if last_launch:
                    last_launch = last_launch[0].date
                    if last_launch + running_delay < datetime.datetime.now():
                        logger.info("Query [%s] restart. Last launch : %s, delay : %s", qu, last_launch, running_delay)
                        qu.status = 0
                else:
                    logger.info("Query [%s] was never launched. Launch it.", qu)
                    qu.status = 0
            if qu.status == 0:
                self.run_query(qu, jsondata)

    def run_query(self, qu, jsondata):
        logger.debug("Running query [%s]", qu)
        try:
            query_result = {}
            qb = QBuilder(logger, make_db_url())
            qb.loadmodels(getattr(settings, 'QBUILDER_MODELS_NAME', 'sample'))
            if jsondata:
                qb.query_parameters = jsondata
                query_result.update({
                    "query_result": qb.all_data(),
                    "sql_query":    str(qb.query),
                    })
                if "statistics" in jsondata:
                    logger.debug("Running statistics for [%s]", qu)
                    query_result["statistics"] = qb.statistics(jsondata.get("percentile", 100), True)
        except:
            logger.error("QBuilder error in query [%s] : %s", qu, traceback.format_exc())
            qu.status = -1 # Erreur execution ou fetch
            qu.save()
            return
        if not query_result["query_result"]:
            logger.info("Query [%s] returned nothing", qu)
            qu.status = 2 # Aucun résultat
            qu.save()
            return
        query_result["keys"] = query_result["query_result"][0].keys()
        try:
            json_data = jsondump(query_result)
        except:
            logger.error("Serializaion error for results of query [%s] : %s", qu, traceback.format_exc())
            qu.status = -2 # Erreur serialization
            qu.save()
            return
        QueryResult.objects.create(query = qu, data = json_data, date = datetime.datetime.now())
        qu.status = 1 # Executé
        qu.save()
        logger.debug("Query [%s] succesfully ran", qu)
