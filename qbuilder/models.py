# -*- coding: utf-8 -*-
from elixir import Field, Interval, Integer
from sqlalchemy.sql import func, cast, extract
from qbuilder.exceptions import *
from django.db import models

class QBEntity(object):
    qbtitle = u"Base model"
    qbdate_criteria = None
    qbfilter = {}
    qbgroup_by = {}
    qbforeigns = {}
    qbdisplay_translations = {}
    qbfield_translations = {}

    @classmethod
    def available_foreigns(cls, models, seen_models = None,indent=0):
        result = {}
        if not seen_models:
            seen_models = [cls.__name__]
        for fk in cls.qbforeigns.keys():
            result[fk] = []
            if fk not in seen_models:
                seen_models.append(fk)
                for fm, fp in getattr(models, fk).available_foreigns(models, seen_models,indent+4).items():
                    if not fm in result.keys():
                        result[fm] = [fk]
                        result[fm].extend(fp)
        for attrname in dir(models):
            attr = getattr(models, attrname)
            if hasattr(attr, 'qbforeigns') and attrname != cls.__name__ and attrname not in seen_models:
                foreigns = getattr(attr, 'qbforeigns')
                if cls.__name__ in foreigns:
                    result[attrname] = []
                    seen_models.append(attrname)
                    for fm, fp in attr.available_foreigns(models, seen_models,indent+4).items():
                        if not fm in result.keys() and fm != cls.__name__:
                            result[fm] = [attrname]
                            result[fm].extend(fp)
        return result

    @classmethod
    def get_join_path(cls, models, to_model):
        path = cls.available_foreigns(models).get(to_model)
        if path is None:
            raise QBIncorrectQuery("Can't join model %s from model %s" % (to_model, cls.__name__))
        path.append(to_model)
        return path

    @classmethod
    def find_foreign_to(cls, models, to_model):
        result = []
        for column in cls.table.columns:
            for fk in column.foreign_keys:
                if fk.column.table == to_model.table:
                    result.append((column, fk.column))
        return result

    @classmethod
    def available_filters(cls):
        return cls.qbfilter

    @classmethod
    def available_group(cls):
        return cls.qbgroup_by

    @classmethod
    def available_date_criteria(cls):
        return cls.qbdate_criteria

    @classmethod
    def translate_field(cls, field):
        return cls.qbfield_translations.get(field, field)

    @classmethod
    def make_filter(cls, field, ftype, value):
        filter = None
        if ftype == 'IN':
            filter = field.in_([v for v in value if v])
        elif ftype == 'date_gt':
            filter = field >  value
        elif ftype == 'date_gte':
            filter = field >= value
        elif ftype == 'date_gt_now_less':
            qty, granularity = value.split(" ")
            filter = field > func.date_trunc(granularity, func.now() - cast(value, Interval()))
        elif ftype == 'date_lt_now_less':
            qty, granularity = value.split(" ")
            filter = field < func.date_trunc(granularity, func.now() - cast(value, Interval()))
        elif ftype == 'date_x_last_n':
            qty, granularity, count_current_period = value.split(" ")
            filter = (field > func.date_trunc(granularity, func.now() - cast("%s %s" % (qty, granularity), Interval())), field < func.date_trunc(granularity, func.now() - cast('0', Interval())),)
            if count_current_period == 'on':
                filter = filter[0]
        elif ftype == 'date_month_ne':
            filter = extract('month', field) != value
        elif ftype == 'date_month_gt':
            filter = extract('month', field) > value
        elif ftype == 'date_month_lt':
            filter = extract('month', field) < value
        elif ftype == 'date_month_eq':
            filter = extract('month', field) == value
        elif ftype == 'date_hour_ne':
            filter = extract('hour', field) != value
        elif ftype == 'date_hour_gt':
            filter = extract('hour', field) > value
        elif ftype == 'date_hour_lt':
            filter = extract('hour', field) < value
        elif ftype == 'date_hour_eq':
            filter = extract('hour', field) == value
        elif ftype == 'date_lt':
            filter = field <  value
        elif ftype == 'date_lte':
            filter = field <= value
        elif ftype == '=':
            filter = field == value
        elif ftype == '!=':
            filter = field != value
        elif ftype == '>':
            filter = field >  value
        elif ftype == '>=':
            filter = field >= value
        elif ftype == '<':
            filter = field <  value
        elif ftype == '<=':
            filter = field <= value
        elif ftype == 'like':
            filter = field.ilike(value)
        return filter

    @classmethod
    def make_grouping(cls, logger, grouping_info):
        group_type, group_args, group_name = grouping_info
        grouping = None
        if group_type == "extract":
            subfield, field_name = group_args
            real_field = getattr(cls, field_name, None)
            if real_field:
                if subfield == 'ampm':
                    grouping = case(whens = [(cast(extract('hour', real_field), Integer()) > 12, 1),], else_ = 0).label(group_name)
                else:
                    grouping = cast(extract(subfield, real_field), Integer()).label(group_name)
            else:
                logger.error("Invalid grouping %s (%s)", grouping_info, cls)
        elif group_type == "date_trunc":
            subfield, field_name = group_args
            real_field = getattr(cls, field_name, None)
            if real_field:
                grouping = func.date_trunc(subfield, real_field)
                grouping = grouping.label(group_name)
            else:
                logger.error("Invalid grouping %s (%s)", grouping_info, cls)
        elif group_type == "func":
            logger.error("Grouping by func not implemented yet")
        elif group_type == 'coalesce_trim':
            # trim(coalesce(field_name, ''))
            field_name = group_args.get('field', group_name)
            real_field = getattr(cls, field_name, None)
            if real_field:
                grouping = func.coalesce(real_field, group_args.get('coalesce_to', ''))
                if group_args.get('trim', True):
                    grouping = func.trim(grouping)
                grouping = grouping.label(group_name)
            else:
                logger.error("Invalid grouping %s (%s)", grouping_info, cls)
        else:
            logger.error("Unknown grouping type %s", group_type)
        return grouping

# Django models
class QueryParameters(models.Model):
    """
    Query parameters saved in BDD
    """

    name  = models.TextField(u"Nom")
    data  = models.TextField(u"Données")
    status = models.IntegerField(u"Statut", default = 0)

    def __unicode__(self):
        return u"%d:%s" % (self.pk, self.name)

    class Meta:
        managed = False
        db_table = 'qbuilder_queryparameters'
        verbose_name = u"Paramètres de requête (Query Builder)"
        verbose_name_plural = u"Paramètres de requêtes (Query Builder)"

class QueryResult(models.Model):
    """
    Query result saved in BDD
    """

    query = models.ForeignKey(QueryParameters)
    data  = models.TextField(u"Données")
    date  = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return u"Results for query %s (executed %s)" % (self.query.name, self.date)

    _indexes = ('query',)
    class Meta:
        managed = False
        db_table = 'qbuilder_result'
        verbose_name = u"Résultat de requête (Query Builder)"
        verbose_name_plural = u"Résultats de requêtes (Query Builder)"

