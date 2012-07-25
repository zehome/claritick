#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
from numpy import average, median, var, std

from elixir import setup_all, DateTime, Interval, Integer, String
from sqlalchemy import create_engine, and_
from sqlalchemy.sql import func, extract, cast, case, literal_column, ClauseElement, exists, select
from sqlalchemy.sql.expression import ColumnClause, _literal_as_column
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

from qbuilder.exceptions import *
from qbuilder.constants import *
from qbuilder.lib import get_granularity, add_granularity_to_date, debug_inline_params
import qbuilder.representations

class OverWindow(ColumnClause):
    """
    The OverWindow creates a column that will render like that :

    SELECT first_value(column_name) OVER (window_clause) FROM table
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
           this is the part we will generate

    Use it like that :
    session.query(OverWindow(table.column_name, windowfunc = 'first_value', windowname = window_clause)

    SEE :
    http://www.postgresql.org/docs/8.4/static/functions-window.html
    """
    def __init__(self, column, **kwargs):
        self.column = column                            # The column that will be used
        self.windowfunc = kwargs.pop('windowfunc', '')  # The 'window function'
        self.windowname = kwargs.pop('windowname', '')  # The WindowClause
        super(OverWindow, self).__init__(column, **kwargs)

@compiles(OverWindow)
def compile_overwindow(element, compiler, **kw):
    """
    Compiles the OverWindow clause (see its doc)
    """
    the_function = getattr(func, element.windowfunc)
    the_raw_column = the_function(element.name)
    return "%s OVER %s" % (the_raw_column, element.windowname)

class WindowClause(ClauseElement):
    """
    The WindowClause creates a clause to use in OverWindow. It will build
    the 'window_clause' part of the OverWindow SQL (see OverWindow doc).

    The generated SQL will look like :

    SELECT .... OVER(PARTITION BY column1,column2 ORDER by column3) FROM table
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                     this is the part we will generate

    Use it like that :
    window_clause = WindowClause(None, 'window_name',  [table.column1, table.column2], [table.column3])

    SEE :
    http://www.postgresql.org/docs/8.4/static/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS
    """
    def __init__(self, select, windowname = 'w', windowpartition = [], windowordering = []):
        self.select = select                    # Unused
        self.windowname = windowname            # Window Name (unused)
        self.windowpartition = windowpartition  # List of PARTITION BY columns
        self.windowordering = windowordering    # List of ORDER BY columns
        super(WindowClause, self).__init__()

@compiles(WindowClause)
def visit_select_with_window(element, compiler, **kw):
    """
    Compiles the WindowClause (see its doc)
    """
    def repr_ordering_column(e):
        if isinstance(e, tuple):
            return "%s %s" % (_literal_as_column(e[0]).label(''), e[1])
        return str(_literal_as_column(e).label(''))
    partition = ordering = ""
    if element.windowpartition:
        partition = "PARTITION BY %s" % ", ".join([str(_literal_as_column(e).label('')) for e in element.windowpartition])
    if element.windowordering:
        ordering = "ORDER BY %s" % ", ".join([repr_ordering_column(e) for e in element.windowordering])
    return "(%s)" % (
        " ".join([partition, ordering,])
        )

class QBuilder(object):
    """
    The main QBuilder class that will load the ORM models, build the SQL
    query from the received instructions, execute the query, make post-processing
    ...
    """

    def __init__(self, logger, databasestring):
        """
        Creates a QBuilder

        Arguments :
        logger : a logger (from the logging module)
        databasestring : the database connection URL
        """
        self.logger = logger
        self.databasestring = databasestring
        self.query_parameters = {}
        # Internal stuff
        self.models = None
        self.selectables = []
        self.eventmodel = None
        self.model_class = None
        self.display_translations = []
        self.granularity = self.granularity_criteria = None
        self.query = self.subquery = self.select_from = None
        self.all_data_store = []
        self.end_date = self.start_date = None
        self.null_as_zero = True
        self.MIN_POINTS = 10
        self.MAX_POINTS  = 200
        self.events_query = None
        self.select_from = None
        self.select = []
        self.filters = []
        self.event_date_filters = []
        self.start_filter = None
        self.end_filter = None
        self.joins = []
        self.group_by = []

    def loadmodels(self, foldername):
        """
        This loads the models from a folder

        See the 'sample' folder to know how to create your own
        database mapping.

        You have to make your models available through __init__
        and you have to declare a QBSelectables and QBEventsConfig
        variables.

        QBSelectables is a list of models the user is allowed to query. The other models are only
        available for joining, filtering or grouping.

        QBEventsConfig is a dictionnary that describes how your event table is (if any).
        """
        try:
            imported = __import__('qbuilder', globals(), locals(), [foldername,])
            self.models = getattr(imported, foldername)
            self.logger.debug("IMPORTED %s", self.models)
            self.selectables = self.models.QBSelectables
            self.QBEventsConfig = self.models.QBEventsConfig
            self.models = self.models.models
            self.logger.debug("Models loaded : %s (selectables : %s)", self.models, self.selectables)
        except (ImportError,), e:
            self.logger.error("Importing models failed : %s", e.args)
        setup_all()

    def has_model(self, modelname):
        if not self.models:
            raise QBNoModelsLoaded()
        return hasattr(self.models, modelname)

    def loadjson(self, filename):
        """
        Load query parameters from JSON file
        """
        with open(filename, "rb") as fp:
            try:
                self.query_parameters = json.load(fp)
            except (ValueError, ), e:
                self.logger.error("Can't load JSON file : %s", (e.args,))
            else:
                self.logger.debug("Parameters loaded : %s", self.query_parameters)

    def check_parameters(self):
        """
        Check that the parameters are correct. This is called by build_query.
        """
        # Main model must exist and must be in selectables
        main_model_name = self.query_parameters.get('model', None)
        if not (main_model_name is not None and self.has_model(main_model_name) and main_model_name in self.selectables):
            raise QBIncorrectModel(main_model_name)
        self.model_class = getattr(self.models, main_model_name)
        for key, value in self.query_parameters.items():
            # Grouping and filtering models must exist
            other_models_names = []
            if (key.startswith('model_for_filter') or key.startswith('model_for_grouping')):
                if not self.has_model(value):
                    raise QBIncorrectModel(value)
                other_models_names.append(value)
            # Filtering fields must exist on their respective models
            if key.startswith('field_for_filter'):
                model_name = self.query_parameters.get(key.replace('field_for_','model_for_'))
                if not model_name:
                    raise QBIncorrectQuery("%s must be associated with a model" % (key,))
                model = getattr(self.models, model_name) # We already checked it exists
                if not hasattr(model, value):
                    raise QBIncorrectQuery("Model %s does not have a %s field (for filtering)" % (model_name, value))
            # Grouping fields must exist on their respective models or be defined in qbgroup_by
            if key.startswith('field_for_grouping'):
                model_name = self.query_parameters.get(key.replace('field_for_','model_for_'))
                if not model_name:
                    raise QBIncorrectQuery("%s must be associated with a model" % (key,))
                model = getattr(self.models, model_name) # We already checked it exists
                if not hasattr(model, value) and not value in model.available_group().keys():
                    raise QBIncorrectQuery("Model %s does not have a %s field (for grouping)" % (model_name, value))
            # Filtering type must be available for filtering field
            if key.startswith('type_for_filter'):
                model_name = self.query_parameters.get(key.replace('type_for_','model_for_'))
                field_name = self.query_parameters.get(key.replace('type_for_','field_for_'))
                if not model_name or not field_name:
                    raise QBIncorrectQuery("%s must be associated with a model and a field" % (key,))
                model = getattr(self.models, model_name) # We already checked it exists
                if value not in model.available_filters().get(field_name, []):
                    raise QBIncorrectQuery("Field %s on model %s does not have a '%s' filtering type" % (field_name, model_name, value))
        # Grouping and filtering models must be related to the main model
        for other_model_name in other_models_names:
            other_model = getattr(self.models, other_model_name)
            if other_model_name != main_model_name and other_model_name not in self.model_class.available_foreigns(self.models) and main_model_name not in other_model.available_foreigns(self.models):
                raise QBIncorrectQuery("Model %s is not related to the main model %s" % (other_model_name, main_model_name))
        # Can't make an "time evolution" query without a date_criteria on the main_model
        if self.query_parameters.get('whattodo', 'count') == 'evolution' and not self.model_class.available_date_criteria():
            raise QBIncorrectQuery("Model %s does not have a date criteria, can't calculate evolution query" % (main_model_name,))

    ###############################
    # Prepare query
    ###############################
    def prepare_query(self):
        """
        This method is called at the very start of the query building process.

        It is used to add automatic columns to the select clause or to prepare
        subqueries that will be used later while building the query.

        It calls the other prepare_query_* depending of the type of query we
        are building.
        """
        self.session = sessionmaker(bind = create_engine(self.databasestring), autocommit=True)()
        whattodo = self.query_parameters.get('whattodo', 'count')
        if whattodo == 'count':
            return self.prepare_query_count()
        elif whattodo == 'evolution':
            return self.prepare_query_evolution()
        elif whattodo == 'select':
            return self.prepare_select()
        elif whattodo == 'tat':
            return self.prepare_tat()
        elif whattodo == 'event_delta':
            return self.prepare_query_event_delta()
        else:
            return False
    def prepare_query_count(self):
        """
        Prepare a 'count' query.

        Adds a 'count(table.primary_key)' in the SELECT
        """
        self.field_to_color = func.count(self.model_class.pk)
        self.select.append(self.field_to_color.label('count'))
        self.display_translations.append(None)
        return True
    def prepare_select(self):
        """
        Prepare a 'select' query.

        Adds the list of fields to the SELECT
        """
        fields = self.query_parameters.get('select_fields', ['pk',])
        if isinstance(fields, basestring):
            fields = fields.split('^')
        for field in fields:
            if '__' in field:
                foreign_model_name, foreign_field = field.split('__') # WARNING : the user has to know the models
                foreign_model = getattr(self.models, foreign_model_name)
                foreign_field = getattr(foreign_model, foreign_field)
                self.select.append(foreign_field)
                self.joins.append(foreign_model_name)
                self.display_translations.append(None)
            else:
                self.select.append(getattr(self.model_class, field))
                self.display_translations.append(None)
        return True
    def prepare_query_evolution(self, add_number_field = True):
        """
        Prepare an 'evolution' query.

        Calculates date filters to avoid querying the whole database.

        The target model must have a date_criteria setting
        """
        if add_number_field:
            self.field_to_color = func.count(self.model_class.pk)
            self.select.append(self.field_to_color.label('count'))
            self.display_translations.append(None)
        # If the user wants to show the evolution of a number but does not give date filters,
        #    we limit the display to a year with a month-granularity
        date_criteria_name = self.model_class.available_date_criteria()
        if date_criteria_name:
            self.date_criteria_field = getattr(self.model_class, date_criteria_name, None)
        if not date_criteria_name or not self.date_criteria_field:
            return False
        self.end_date     = datetime.datetime.now()
        self.start_date   = self.end_date - datetime.timedelta(days = 365)
        self.start_filter = self.date_criteria_field > self.start_date
        self.end_filter   = self.date_criteria_field < self.end_date
        return True
    def prepare_tat(self):
        """
        Prepare a 'tat' query

        Here we build a big 'windowed' subquery that calculates the deltas between
        the events
        """
        partition_field = getattr(self.eventmodel, self.QBEventsConfig.get('partition_field', 'partition_field'))
        event_type_field = getattr(self.eventmodel, self.QBEventsConfig.get('event_type', 'event_type'))
        event_date_field = getattr(self.eventmodel, self.QBEventsConfig.get('event_date', 'event_date'))
        first_subq_filters = []
        event_filters = []
        if 'starting_event_choice' in self.query_parameters:
            ec = self.query_parameters.get('starting_event_choice')
            if not isinstance(ec, (list, tuple)):
                ec = [ec,]
            event_filters.extend(ec)
            first_subq_filters.append(_literal_as_column('main_event_type').in_(ec))
        last_subq_filters = []
        if 'ending_event_choice' in self.query_parameters:
            ec = self.query_parameters.get('ending_event_choice')
            if not isinstance(ec, (list, tuple)):
                ec = [ec,]
            event_filters.extend(ec)
            last_subq_filters.append(_literal_as_column('main_event_type').in_(ec))
        if event_filters:
            event_filters = [event_type_field.in_(event_filters)]
        event_filters.extend(self.event_date_filters)
        self.main_subquery = self.session.query(
            (event_date_field - OverWindow(event_date_field, windowfunc = 'first_value', windowname = WindowClause(None, 'o', [partition_field], [event_date_field]))).label('main_event_delta'),
            partition_field.label('main_partition_field'),
            event_type_field.label('main_event_type'),
            ).filter(and_(*event_filters))
        return True
    def prepare_query_event_delta(self):
        """
        Prepare a 'event_delta' query.

        Here we build a big 'windowed' subquery that calculates the delta between
        the first event of one type and the last event of another type.

        This subquery will be used later in build_events_query.
        """
        # Build the 'first_event_of_this_type' and 'last_event_of_this_type' queries
        # We need to know the 'event model' fields. Grab it from QBEventsConfig
        partition_field = getattr(self.eventmodel, self.QBEventsConfig.get('partition_field', 'partition_field'))
        event_type_field = getattr(self.eventmodel, self.QBEventsConfig.get('event_type', 'event_type'))
        event_date_field = getattr(self.eventmodel, self.QBEventsConfig.get('event_date', 'event_date'))
        # This 'main_subquery' calculates the delta between the 'current' event and the first event
        # for the current 'partition_field' entity
        self.main_subquery = self.session.query(
            partition_field.label('main_partition_field'),
            event_type_field.label('main_event_type'),
            event_date_field.label('main_event_date'),
            (event_date_field - OverWindow(event_date_field, windowfunc = 'first_value', windowname = WindowClause(None, 'o', [partition_field], [event_date_field]))).label('main_event_delta')
            ).filter(and_(*self.event_date_filters)).subquery()
        # Prepare the two window clauses
        first_event_window = WindowClause(None, 'first', [_literal_as_column('main_partition_field'), _literal_as_column('main_event_type')], [(_literal_as_column('main_event_date'), 'ASC')])
        last_event_window  = WindowClause(None, 'last',  [_literal_as_column('main_partition_field'), _literal_as_column('main_event_type')], [(_literal_as_column('main_event_date'), 'DESC')])
        # Build the two subqueries (One for 'first event of this type' and the other for 'last event of this type')
        first_subq_filters = []
        if 'starting_event_choice' in self.query_parameters:
            ec = self.query_parameters.get('starting_event_choice')
            if not isinstance(ec, (list, tuple)):
                ec = [ec,]
            first_subq_filters.append(_literal_as_column('main_event_type').in_(ec))
        first_subq = self.session.query(
            OverWindow(_literal_as_column('main_partition_field'), windowfunc = 'first_value', windowname = first_event_window).label('first_event_partition_field'),
            OverWindow(_literal_as_column('main_event_type'),  windowfunc = 'first_value', windowname = first_event_window).label('first_event_type'),
            OverWindow(_literal_as_column('main_event_date'),  windowfunc = 'first_value', windowname = first_event_window).label('first_event_date'),
            OverWindow(_literal_as_column('main_event_delta'), windowfunc = 'first_value', windowname = first_event_window).label('first_event_delta'),
            ).select_from(self.main_subquery).filter(and_(*first_subq_filters)).distinct().subquery()
        last_subq_filters = []
        if 'ending_event_choice' in self.query_parameters:
            ec = self.query_parameters.get('ending_event_choice')
            if not isinstance(ec, (list, tuple)):
                ec = [ec,]
            last_subq_filters.append(_literal_as_column('main_event_type').in_(ec))
        last_subq = self.session.query(
            OverWindow(_literal_as_column('main_partition_field'), windowfunc = 'first_value', windowname = last_event_window).label('last_event_partition_field'),
            OverWindow(_literal_as_column('main_event_type'),  windowfunc = 'first_value', windowname = last_event_window).label('last_event_type'),
            OverWindow(_literal_as_column('main_event_date'),  windowfunc = 'first_value', windowname = last_event_window).label('last_event_date'),
            OverWindow(_literal_as_column('main_event_delta'), windowfunc = 'first_value', windowname = last_event_window).label('last_event_delta'),
            ).select_from(self.main_subquery).filter(and_(*last_subq_filters)).distinct().subquery()
        # Join them
        joined = first_subq.join(last_subq, _literal_as_column('first_event_partition_field') == _literal_as_column('last_event_partition_field'))
        # And generate the events_query that calculates the delta between the first
        # event of a type and the last event of another type
        # We only keep values > 0 because we don't want to reverse time
        self.events_query = self.session.query(
            _literal_as_column('first_event_partition_field'),
            _literal_as_column('first_event_date'),
            _literal_as_column('last_event_date'),
            _literal_as_column('first_event_type'),
            _literal_as_column('last_event_type'),
            _literal_as_column('first_event_delta'),
            _literal_as_column('last_event_delta'),
            (_literal_as_column('last_event_delta') - _literal_as_column('first_event_delta')).label('deltas_delta')
            ).select_from(joined)
        self.events_query = self.events_query.filter((_literal_as_column('last_event_delta') - _literal_as_column('first_event_delta')) > '0').order_by('last_event_date').subquery()
        self.select.insert(0, partition_field) # We HAVE TO select this field
        return True
    def prepare_filters_and_grouping(self):
        """
        Parse the filters and grouping parameters, keep
        the user defined order.
        """
        filter_nbs = []
        grouping_nbs = []
        for key, value in self.query_parameters.items():
            if key.startswith('value_for_filter_'):
                filter_nb = key.split('_')[3]
                if key.endswith('[]'):
                    filter_nb = filter_nb[:-2]
                filter_nbs.append((int(filter_nb), value))
            elif key.startswith('field_for_grouping_'):
                grouping_nbs.append((int(key.split('_')[3]), value))
            filter_nbs.sort(lambda a,b: cmp(a[0],b[0]))
            grouping_nbs.sort(lambda a,b: cmp(a[0],b[0]))
        return filter_nbs, grouping_nbs
    def generate_filters(self, filter_nbs):
        """
        For each filter parameter in the user request, we prepare
        the statement

        We add each model we filter on in the list of tables we need to join with.
        """
        whattodo = self.query_parameters.get('whattodo', None)
        for filter_nb, value in filter_nbs:
            foreign_model = foreignkey_to_model = foreignfield = filter_type = None
            this_filter = None
            foreign_model       = getattr(self.models, self.query_parameters.get('model_for_filter_%s' % (filter_nb,), None))
            foreignfield        = getattr(foreign_model, self.query_parameters.get('field_for_filter_%s' % (filter_nb,), None), None)
            filter_type         = self.query_parameters.get('type_for_filter_%s'  % (filter_nb,), None)
            if foreignfield and filter_type:
                # Make filter can return one or many filters
                # SEE qbuilder/models.py if needed
                this_filters = self.model_class.make_filter(foreignfield, filter_type, value)
                self.logger.debug("Filter made from %s, %s, %s : %s", foreignfield, filter_type, value, this_filters)
                if not isinstance(this_filters, tuple):
                    # Make filter only returned one filter
                    this_filters = [this_filters,]
                for this_filter in this_filters:
                    # TODO : check and document the specific cases below
                    if this_filter is not None:
                        if whattodo in ('evolution', 'event_delta_evolution') and foreignfield.key == self.model_class.available_date_criteria() and filter_type in ('date_gt', 'date_gte'):
                            self.start_date   = datetime.datetime.strptime(value, '%Y-%m-%d')
                            self.start_filter = this_filter
                        elif whattodo in ('evolution', 'event_delta_evolution') and foreignfield.key == self.model_class.available_date_criteria() and filter_type in ('date_lt', 'date_lte'):
                            self.end_date   = datetime.datetime.strptime(value, '%Y-%m-%d')
                            self.end_filter = this_filter
                        elif whattodo in ('evolution', 'event_delta_evolution') and foreignfield.key == self.model_class.available_date_criteria() and filter_type == 'date_gt_now_less':
                            qty, type = value.split(" ")
                            self.start_date   = add_granularity_to_date(datetime.datetime.now(), type, float(qty))
                            self.start_filter = this_filter
                        elif whattodo in ('evolution', 'event_delta_evolution') and foreignfield.key == self.model_class.available_date_criteria() and filter_type == 'date_lt_now_less':
                            qty, type = value.split(" ")
                            self.end_date   = add_granularity_to_date(datetime.datetime.now(), type, -float(qty))
                            self.end_filter = this_filter
                        else:
                            self.filters.append(this_filter)
                            if self.model_class != foreign_model and foreign_model not in self.joins:
                                for joining_model in self.model_class.get_join_path(self.models, foreign_model.__name__):
                                    if not joining_model in self.joins:
                                        self.joins.append(joining_model)
    def generate_prefilters(self, filter_nbs):
        """
        For each filter parameter in the user request, we check if it's a filter on
        the event's date.

        If so, we remove the filter from the list and create a event_date_filter
        """
        whattodo = self.query_parameters.get('whattodo', None)
        if whattodo not in ('event_delta', 'event_delta_evolution', 'tat'):
            return filter_nbs
        event_date_field = getattr(self.eventmodel, self.QBEventsConfig.get('event_date', 'event_date'))
        new_filter_nbs = []
        for filter_nb, value in filter_nbs:
            foreign_model = getattr(self.models, self.query_parameters.get('model_for_filter_%s' % (filter_nb,), None))
            foreignfield  = getattr(foreign_model, self.query_parameters.get('field_for_filter_%s' % (filter_nb,), None), None)
            filtertype    = self.query_parameters.get('type_for_filter_%s' % (filter_nb,), None)
            if foreignfield == event_date_field:
                self.event_date_filters.append(foreign_model.make_filter(foreignfield, filtertype, value))
            else:
                new_filter_nbs.append((filter_nb, value))
        return new_filter_nbs
    def generate_groupings(self, grouping_nbs):
        """
        Generate all the group by clause

        We add each model in the 'groupings' to the tables we need to join with
        and we add each column we group on in the selected columns.
        """
        for index, (grouping_nb, value) in enumerate(grouping_nbs):
            this_grouping = foreignkey_to_model = translation = None
            foreign_model = getattr(self.models, self.query_parameters.get('model_for_grouping_%s' % (grouping_nb,), None))
            foreignfield_name = self.query_parameters.get('field_for_grouping_%s' % (grouping_nb,), None)
            foreignfield = getattr(foreign_model, foreignfield_name, None)
            grouping_type = self.query_parameters.get('type_for_grouping_%s'  % (grouping_nb,), None)
            grouping_value = self.query_parameters.get('value_for_grouping_%s' % (grouping_nb,), None)
            translation = foreign_model.qbdisplay_translations.get(foreignfield_name, None)
            if foreign_model:
                if grouping_type is not None and grouping_value is not None:
                    filters = [foreignfield == grouping_value]
                    fk_to_model = foreign_model.find_foreign_to(self.models, self.model_class)
                    for fk_from, fk_to in fk_to_model:
                        filters.append(fk_from == fk_to)
                    stmt = self.session.query(foreignfield)
                    for filter in filters:
                        stmt = stmt.filter(filter)
                    stmt = exists(stmt.correlate(self.model_class).statement).label('grouping_1')
                    self.select.append(stmt)
                    self.group_by.append(stmt)
                else:
                    grouping_info = foreign_model.available_group().get(foreignfield_name, None)
                    if grouping_info and isinstance(grouping_info[1], (tuple, list)):
                        this_grouping = foreign_model.make_grouping(self.logger, grouping_info[1])
                    elif foreignfield:
                        this_grouping = foreignfield
                    if this_grouping is not None:
                        self.group_by.append(this_grouping)
                        self.select.append(this_grouping)
                        self.display_translations.append(translation)
                        if self.model_class != foreign_model and foreign_model not in self.joins:
                            for joining_model in self.model_class.get_join_path(self.models, foreign_model.__name__):
                                if not joining_model in self.joins:
                                    self.joins.append(joining_model)

    ###############################
    # JSON -> SQL (build the query)
    ###############################
    def build_query(self):
        """
        This is where all the magic happens

        TODO : split this in many sub routines.
        """
        if not self.query_parameters:
            self.logger.error("Can't build query without parameters. Please load a JSON file or a query from BDD.")
        try:
            self.check_parameters()
        except (QBException,),e:
            self.logger.error("Can't build query with bad parameters : %s", e)
            return

        # Prepare the query and the specific stuff depending on the 'whattodo'
        filter_nbs, grouping_nbs = self.prepare_filters_and_grouping()
        filter_nbs = self.generate_prefilters(filter_nbs)
        self.prepare_query()
        # Prepare and generate the filters and grouping
        self.generate_filters(filter_nbs)
        self.generate_groupings(grouping_nbs)
        # Decide of the correct granularity when displaying evolutions
        if self.granularity_criteria is None and self.query_parameters.get("whattodo", "count") in ('evolution', 'event_delta_evolution'):
            date_delta = self.end_date - self.start_date
            self.granularity = get_granularity(date_delta, self.MIN_POINTS, self.MAX_POINTS)#'month'
            self.granularity_criteria = func.date_trunc(self.granularity, self.date_criteria_field).label("Date")
        # A specific granularity has speen specified or decided, generate
        # a subquery with generate_series to avoid holes in the time
        if self.granularity_criteria is not None:
            self.subquery = self.session.query(func.generate_series(func.date_trunc(self.granularity, cast(self.start_date, DateTime())), func.date_trunc(self.granularity, cast(self.end_date, DateTime())), cast('1 %s' % self.granularity, Interval())).label('Temps')).subquery()
            self.select.insert(1,self.granularity_criteria)
            self.display_translations.insert(1, None)
            self.group_by.insert(0,self.granularity_criteria)
        ### Extras ###
        # The user specified a boundary
        extras = self.query_parameters.get("extras", {})
        if extras and 'boundary' in self.extras:
            boundary_max = extras.get('boundary', {}).get('max', None)
            classes_case = []
            if boundary_max and self.field_to_color is not None:
                classes_case.append((self.field_to_color > boundary_max, literal_column("'breaks_max_bound'",String)))
            boundary_min = extras.get('boundary', {}).get('min', None)
            if boundary_min and self.field_to_color is not None:
                classes_case.append((self.field_to_color < boundary_min, literal_column("'breaks_min_bound'",String)))
            self.select.append(case(classes_case).label("_classes_"))
            self.display_translations.append(None)
        date_compare = extras.get('option', {}).get('date_compare', 'No')
        if date_compare != 'No':
            # This is used to decide how to regroup the data depending of what is
            # on the 'X' axis
            criteria_mapping = {
                'second' : ('minute', 'Minute'),
                'minute' : ('hour', 'Hour'),
                'hour'   : ('day', 'Day'),
                'dow'    : ('week', 'Week'),
                'day'    : ('month', 'Month'),
                'week'   : ('year', 'Year'),
                'month'  : ('year', 'Year'),
                }
            rebuilded_select = []
            # TODO : Sûrement améliorable :
            for index, statement in enumerate(self.select):
                first_base_column = list(statement.base_columns)[0]
                if hasattr(first_base_column, 'name') and first_base_column.name == 'date_trunc':
                    statement = func.date_part(self.granularity, statement).label(self.granularity)
                    extract_criteria = criteria_mapping.get(self.granularity, ('year', u'Année'))
                    self.group_by.append(extract(extract_criteria[0], self.date_criteria_field))
                    rebuilded_select.append(statement)
                    rebuilded_select.append(cast(extract(extract_criteria[0], self.date_criteria_field), Integer()).label(extract_criteria[1]))
                else:
                    rebuilded_select.append(statement)
            self.select = rebuilded_select
        # Here is what we have generated so far
        self.logger.debug("SELECT %s JOIN %s FILTERS %s %s %s GROUP BY %s",self.select,self.joins,self.start_filter, self.end_filter, self.filters,self.group_by)
        # Alias identically named columns
        already_seen_names = []
        new_select = []
        for column in self.select:
            if column.key in already_seen_names:
                new_select.append(column.label('%s_%s' % (column.parententity.mapped_table.name, column.key)))
            else:
                new_select.append(column)
                already_seen_names.append(column.key)
        self.select = new_select
        # Finally : make the query by appending all this stuff together
        if self.events_query is not None:
            self.query = self.build_events_query()
        elif self.query_parameters.get('whattodo','count') == 'tat':
            self.query = self.main_subquery
        else:
            self.query = self.session.query(*self.select)
            if self.select_from is not None:
                self.query = self.query.select_from(self.select_from)
            if self.joins:
                self.query = self.query.join(*[getattr(self.models, model_name) for model_name in self.joins])
            if self.start_filter is not None:
                self.filters.append(self.start_filter)
            if self.end_filter is not None:
                self.filters.append(self.end_filter)
            for filter in self.filters:
                self.query = self.query.filter(filter)
            if self.group_by:
                self.query = self.query.group_by(*self.group_by)
            if self.subquery is not None:
                stmt1 = self.subquery
                stmt2 = self.query.subquery()
                # Column order : Y, X, (Z)
                stmt2columns = stmt2.c.keys()
                yvalue_column = stmt2columns.pop(0)
                grouping_column = stmt2columns.pop(0)
                self.select_from = stmt1.outerjoin(stmt2, stmt1.c.Temps == stmt2.c[grouping_column])
                ycolumn = stmt2.c[yvalue_column]
                if self.null_as_zero:
                    ycolumn = case([(ycolumn == None, 0),], else_ = ycolumn).label(yvalue_column)
                columns = [ycolumn, stmt1.c.Temps]
                # If we have remaining columns, select them now
                if stmt2columns:
                    columns.extend([stmt2.c[k] for k in stmt2columns])
                self.query = self.session.query(*columns)

        # Default ordering
        # TODO : find a smart ordering algo
        order_columns = range(3, len(self.query.column_descriptions)+1)
        order_columns.append(2)
        self.query = self.query.order_by(*[str(oc) for oc in order_columns])
        self.save_query()
        self.logger.debug("Built Query : %s", str(debug_inline_params(self.query)))
        return self.query
    def build_events_query(self):
        """
        With the 'events' based query, it's pretty different
        """
        if self.events_query is None:
            return None
        left_subquery = self.session.query(*self.select)
        if self.joins:
            left_subquery = left_subquery.join(*[getattr(self.models, model_name) for model_name in self.joins])
        left_subquery = left_subquery.subquery()
        right_subquery = self.events_query
        wanna_see = [right_subquery.columns.deltas_delta, right_subquery.columns.last_event_date,]
        joint = left_subquery.join(right_subquery, right_subquery.columns.first_event_partition_field == left_subquery.columns.get(self.QBEventsConfig['partition_field']))
        new_group_by = wanna_see[:]
        if self.group_by:
            hasher = {}
            for c in left_subquery.columns:
                hasher[c.key] = c
            for grby in self.group_by:
                if hasattr(grby, "parententity"):
                    new_group_by.append(hasher.get("%s_%s" % (grby.parententity.mapped_table.name, grby.key), hasher.get("%s" % (grby.key,))))
                else:
                    new_group_by.append(hasher.get("%s" % (grby.name,)))
        # We remove the first member of self.select because we added it
        # "automatically" to allow the rest of the query builder to work
        columns = wanna_see
        for index, column in enumerate(left_subquery.columns):
            if index != 0:
                columns.append(column)
        #columns.extend(right_subquery.columns)
        built_query = self.session.query(*columns).select_from(joint)
        if new_group_by:
            built_query = built_query.group_by(*new_group_by)
        built_query = built_query.order_by(right_subquery.columns.last_event_date)
        return built_query

    def all_data(self):
        if not self.query:
            self.build_query()
        if not self.query:
            return []
        if not self.all_data_store:
            self.all_data_store = self.query.all()
        return self.all_data_store

    ########################
    # POST - PROCESSING    #
    ########################
    def data_cmp(self, data, rang_MAX, rang_MIN, n_colum):
        tmp_data = [[tup, index] for index, tup in enumerate(data)]
        tmp_data.sort(lambda a, b: cmp(a[0],b[0]))
        tmp_data = tmp_data[rang_MIN - 1:rang_MAX]
        tmp_data.sort(lambda a, b: cmp(a[1], b[1]))
        return tmp_data

    def convert_timedelta_to_float(self, st_time):
        value_time = st_time.seconds + st_time.microseconds / 1000000 + st_time.days * 60 * 60 * 24
        return value_time

    def convert_float_to_timedelta(self, value_time):
        tmdelta = datetime.timedelta(seconds = value_time)
        return tmdelta

    def check_args_stats(self, data, percentile, n_colum):
        if data == []:
            raise QBEmptyDatabase("Can't build statistics with empty database")
        try:
            percentile = float(percentile)
            if percentile <= 50. or percentile > 100:
                raise QBPercentile("Usage: percentile must be between 51 to 100")
        except ValueError:
            raise QBArgs("Invalid type parameter")
        try:
            n_colum = int(n_colum)
        except ValueError:
            raise QBArgs("Invalid type parameter")
        return percentile, n_colum

    def built_stats(self, data, percentile = 100, n_colum = 1):
        flag_timedelta = False
        #self.logger.debug("Print data: %s", data)
        percentile, n_colum = self.check_args_stats(data, percentile, n_colum)
        filterdata = []
        for elt in data:
            filterdata.append(elt[n_colum])
        #self.logger.debug("Print filterdata: %s", filterdata)
        len_db = len(filterdata)
        if percentile < 100:
            rang_MAX = (percentile / 100.) * len(filterdata) + 0.5 
            rang_MIN = ((100. - percentile) / 100.) * len(filterdata) + 0.5
            rang_MAX = int(round(rang_MAX))
            rang_MIN = int(round(rang_MIN))
            data = self.data_cmp(filterdata, rang_MAX, rang_MIN, n_colum)
            nwdata = []
            for elt in data:
                nwdata.append(elt[0])
            data = nwdata
            #self.logger.debug("Print data after Percentile: %s", data)
            if data == []:
                raise QBEmptyDatabase("Can't build statistics with empty database")
        else:
            data = filterdata
        if isinstance(data[0], datetime.timedelta):
            flag_timedelta = True
            data = [self.convert_timedelta_to_float(index) for index in data]
        len_dbper = len(data)
        value_MAX = max([index for index in data])
        value_MIN = min([index for index in data])
        value_average = average([index for index in data])
        value_median = median([index for index in data])
        value_variance = var([index for index in data])
        ecart_type = std([index for index in data])
        if flag_timedelta:
            value_MAX = self.convert_float_to_timedelta(value_MAX)
            value_MIN = self.convert_float_to_timedelta(value_MIN)
            value_average = self.convert_float_to_timedelta(value_average)
            value_median = self.convert_float_to_timedelta(value_median)
            value_variance = self.convert_float_to_timedelta(value_variance)
            ecart_type = self.convert_float_to_timedelta(ecart_type)
        result = {
            QB_STYPE_MAX:value_MAX,
            QB_STYPE_MIN:value_MIN,
            QB_STYPE_AVG:value_average,
            QB_STYPE_MED:value_median,
            QB_STYPE_VAR:value_variance,
            QB_STYPE_STD:ecart_type,
            QB_STYPE_CNT:len_db,
            QB_STYPE_CRP:len_dbper,
            }
        return result

    def sort_data(self, data):
        mddata = [[row[1:], row[0]] for row in data]
        save_param = []
        index = 0
        while index < len(mddata):
            if save_param == []:
                save_param.append(mddata[index][0])
            if mddata[index][0] not in save_param:
                save_param.append(mddata[index][0])
            index += 1
        index = 0
        categorie_list = []
        while index < len(save_param):
            ref = save_param[index]
            index2 = 0
            tmp_list = []
            while index2 < len(mddata):
                if ref == mddata[index2][0]:
                    tmp_list.append(mddata[index2])
                index2 += 1
            categorie_list.append(tmp_list)
            index += 1
        return categorie_list

    def make_hashed_data(self, data, x_column = 0, y_column = 1, first_z_column = 2, last_z_column = 3):
        # data : [(X,Y,Z1),(X,Y,Z2)]
        # result {Z1:[(X,Y),(X,Y)],Z2:[(X,Y),(X,Y)]}
        result = {}
        for line in data:
            z = line[first_z_column:last_z_column]
            y = line[y_column]
            x = line[x_column]
            result.setdefault(z,[]).append([x,y])
        return result

    def statistics(self, percentile, flag_sort = False):
        # Si flag_sort False, la fonction sera appelee sans "tri" preliminaire
        data = self.all_data()
        if not data:
            return {}
        if flag_sort:
            datasorted = self.make_hashed_data(data, 1, 0, 2, len(data[0]))
            result = {}
            for hash_key, datalist in datasorted.iteritems():
                if isinstance(hash_key, (tuple, list)):
                    hash_key = u" ".join([str(k) for k in hash_key])
                try:
                    result[hash_key] = self.built_stats(datalist, percentile)
                except (QBException,):
                    self.logger.error("Can't build statistics with bad arguments")
                    result[hash_key] = None
            return result

        try:
            return self.built_stats(data, percentile, 0) # "0" => numero de colonne a traite, a rendre parametrable
        except (QBException,):
            self.logger.error("Can't build statistics with bad arguments")
            return {}

    def save_query(self):
        pass

def main(options, logger, *args):
    qb = QBuilder(logger, "postgresql+psycopg2://" + options.databaseurl)
    qb.loadmodels(options.modelsfolder)

    if options.jsonfile:
        qb.loadjson(options.jsonfile)
    if options.build_query:
        print qb.build_query()
    if options.get_data:
        print qb.all_data()
        ## Highcharts ## A Enlever
        data = qb.all_data()
        fp = open("datajson", "wb+")
        fp.write(json.dumps(data))
        fp.close()
    if options.statistics:
        print qb.statistics(options.statistics)
    if options.representation:
        repr_class = getattr(qbuilder.representations, options.representation, getattr(qbuilder.representations, "%sRepresentation" % (options.representation,), None))
        if repr_class is None:
            logger.error(u"None of %s nor %s exists. Using the default TextRepresentation")
            repr_class = qbuilder.representations.TextRepresentation
        representation = repr_class(qb, logger)
        representation.represent()
