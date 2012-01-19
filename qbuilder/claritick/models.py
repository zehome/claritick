# -*- coding: utf-8 -*-
from qbuilder.models import QBEntity
from elixir import Entity, using_options, using_table_options, Field
from elixir import Integer, String, Float, DateTime, Boolean, Interval
from elixir import ManyToOne, OneToMany

ALL_DATE_FILTERS = (
    'date_gt',
    'date_lt',
    'date_gt_now_less',
    'date_lt_now_less',
    'date_hour_gt',
    'date_hour_lt',
    'date_hour_eq',
    'date_hour_ne',
    'date_month_gt',
    'date_month_lt',
    'date_month_eq',
    'date_month_ne',
    '=',
    '!=',
    )

STD_FILTERS = ('=','!=','IN', '>', '<')

class VueTicketsTempsCloture(Entity, QBEntity):
    # options
    using_options(tablename = 'temps_cloture', allowcoloverride=True)

    # fields
    pk = Field(Integer, primary_key = True, colname = 'id')
    date_open = Field(DateTime)
    date_close = Field(DateTime)
    temps_cloture = Field(Interval)

    # QB properties
    qbtitle = u'tickets'
    qbfilter = {
        'date_close' : ALL_DATE_FILTERS,
        'date_open' : ALL_DATE_FILTERS,
        'temps_cloture' : ('=', '!=',),
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

class State(Entity, QBEntity):
    using_options(tablename = 'ticket_state', allowcoloverride = True)

    pk = Field(Integer, primary_key = True, colname = 'id')
    label = Field(String)
    weight = Field(Integer)

    qbtitle = u'status'
    qbfilter = {
        'pk' : STD_FILTERS,
        'label' : STD_FILTERS,
        'weight' : STD_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

class Priority(Entity, QBEntity):
    using_options(tablename = 'ticket_priority', allowcoloverride = True)

    pk = Field(Integer, primary_key = True, colname = 'id')
    label = Field(String)

    qbtitle = u'priorité'
    qbfilter = {
        'pk' : STD_FILTERS,
        'label' : STD_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

class Category(Entity, QBEntity):
    using_options(tablename = 'ticket_category', allowcoloverride = True)

    pk = Field(Integer, primary_key = True, colname = 'id')
    label = Field(String)

    qbtitle = u'catégorie'
    qbfilter = {
        'pk' : STD_FILTERS,
        'label' : STD_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

class TickUser(Entity, QBEntity):
    using_options(tablename = 'auth_user', allowcoloverride = True)

    pk = Field(Integer, primary_key = True, colname = 'id')
    username     = Field(String)
    first_name   = Field(String)
    last_name    = Field(String)
    email        = Field(String)
    is_active    = Field(Boolean)
    is_superuser = Field(Boolean)
    last_login   = Field(DateTime)
    date_joined  = Field(DateTime)

    qbtitle = u'utilisateur'
    qbfilter = {
        'pk' : STD_FILTERS,
        'username' : STD_FILTERS,
        'first_name' : STD_FILTERS,
        'last_name' : STD_FILTERS,
        'email' : STD_FILTERS,
        'is_active' : STD_FILTERS,
        'is_superuser' : STD_FILTERS,
        'last_login' : ALL_DATE_FILTERS,
        'date_joined' : ALL_DATE_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

class Tickets(Entity, QBEntity):
    using_options(tablename = 'tickets_clarisys', allowcoloverride = True)

    pk                  = Field(Integer, primary_key = True, colname = 'id')
    client_id           = Field(Integer)
    contact             = Field(String)
    telephone           = Field(String)
    date_open           = Field(DateTime)
    last_modification   = Field(DateTime)
    date_close          = Field(DateTime)
    State               = ManyToOne(State, colname = 'state_id', target_column = 'id')
    Priority            = ManyToOne(Priority, colname = 'priority_id', target_column = 'id')
    TickUser            = ManyToOne(TickUser, colname = 'assigned_to_id', target_column = 'id')
    opened_by_id        = Field(Integer)
    title               = Field(String)
    text                = Field(String)
    Category            = ManyToOne(Category, colname = 'category_id', target_column = 'id')
    project_id          = Field(Integer)
    validated_by_id     = Field(Integer)
    keywords            = Field(String)
    calendar_start_time = Field(DateTime)
    calendar_end_time   = Field(DateTime)
    calendar_title      = Field(String)
    template            = Field(Boolean)
    nb_comments         = Field(Integer)
    parent_id           = Field(Integer)
    diffusion           = Field(Boolean)
    nb_appels           = Field(Integer)
    message_id          = Field(String)

    qbtitle = u"tickets"
    qbfilter = {
        'date_close': ALL_DATE_FILTERS,
        'date_open': ALL_DATE_FILTERS,
        'state_id': STD_FILTERS,
        'category_id': STD_FILTERS,
        'priority_id': STD_FILTERS,
        'assigned_to_id': STD_FILTERS,
        'opened_by_id': STD_FILTERS,
        }
    qbforeigns = {
        'TickUser' : [],
        'State' : [],
        'Priority': [],
        'Category': [],
        }
    qbgroup_by = {
        'dateo'       : (u'date', ('date_trunc', ('day', 'date_open'), u"Date d'ouverture"), False),
        'dateo_week'  : (u'date (num semaine)', ('date_trunc', ('week', 'date_open'), u"Semaine"), False),
        'dateo_hour'  : (u'date (heure)', ('date_trunc', ('hour', 'date_open'), u"Heure d'ouverture"), False),
        'dateo_day'   : (u'date (jour du mois)', ('date_trunc', ('day', 'date_open'), u"Jour"), False),
        'dateo_dow'   : (u'date (jour de la semaine)', ('date_trunc', ('dow', 'date_open'), u"Jour"), False),
        'dateo_month' : (u'date (mois)', ('date_trunc', ('month', 'date_open'), u"Mois d'ouverture"), False),
        'dateo_year'  : (u'date (année)', ('date_trunc', ('year', 'date_open'), u"Annee d'ouverture"), False),
        'dateo_half'  : (u'date (am/pm)', ('date_trunc', ('ampm', 'date_open'), u'Demi journée'), False),
        }
    qbfield_translations = {
        }

class TicketsClarisysSiemens(Entity, QBEntity):
    using_options(tablename = 'tickets_clarisys_siemens', allowcoloverride = True)

    pk                  = Field(Integer, primary_key = True, colname = 'id')
    client_id           = Field(Integer)
    contact             = Field(String)
    telephone           = Field(String)
    date_open           = Field(DateTime)
    last_modification   = Field(DateTime)
    date_close          = Field(DateTime)
    State               = ManyToOne(State, colname = 'state_id', target_column = 'id')
    Priority            = ManyToOne(Priority, colname = 'priority_id', target_column = 'id')
    TickUser            = ManyToOne(TickUser, colname = 'assigned_to_id', target_column = 'id')
    opened_by_id        = Field(Integer)
    title               = Field(String)
    text                = Field(String)
    Category            = ManyToOne(Category, colname = 'category_id', target_column = 'id')
    project_id          = Field(Integer)
    validated_by_id     = Field(Integer)
    keywords            = Field(String)
    calendar_start_time = Field(DateTime)
    calendar_end_time   = Field(DateTime)
    calendar_title      = Field(String)
    template            = Field(Boolean)
    nb_comments         = Field(Integer)
    parent_id           = Field(Integer)
    diffusion           = Field(Boolean)
    nb_appels           = Field(Integer)
    message_id          = Field(String)
    ticket_siemens      = Field(Boolean)
    temps_cloture       = Field(Interval)

    qbtitle = u"tickets"
    qbfilter = {
        'date_close': ALL_DATE_FILTERS,
        'date_open': ALL_DATE_FILTERS,
        'state_id': STD_FILTERS,
        'category_id': STD_FILTERS,
        'priority_id': STD_FILTERS,
        'assigned_to_id': STD_FILTERS,
        'opened_by_id': STD_FILTERS,
        'ticket_siemens': STD_FILTERS,
        'temps_cloture': STD_FILTERS,
        }
    qbforeigns = {
        'TickUser' : [],
        'State' : [],
        'Priority': [],
        'Category': [],
        }
    qbgroup_by = {
        'dateo'       : (u'date', ('date_trunc', ('day', 'date_open'), u"Date d'ouverture"), False),
        'dateo_week'  : (u'date (num semaine)', ('date_trunc', ('week', 'date_open'), u"Semaine"), False),
        'dateo_hour'  : (u'date (heure)', ('date_trunc', ('hour', 'date_open'), u"Heure d'ouverture"), False),
        'dateo_day'   : (u'date (jour du mois)', ('date_trunc', ('day', 'date_open'), u"Jour"), False),
        'dateo_dow'   : (u'date (jour de la semaine)', ('date_trunc', ('dow', 'date_open'), u"Jour"), False),
        'dateo_month' : (u'date (mois)', ('date_trunc', ('month', 'date_open'), u"Mois d'ouverture"), False),
        'dateo_year'  : (u'date (année)', ('date_trunc', ('year', 'date_open'), u"Annee d'ouverture"), False),
        'dateo_half'  : (u'date (am/pm)', ('date_trunc', ('ampm', 'date_open'), u'Demi journée'), False),
        }
    qbfield_translations = {
        }

class CloturesDansLaJournee(Entity, QBEntity):
    # options
    using_options(tablename = 'clotures_dans_la_journee', allowcoloverride=True)

    # fields
    jour = Field(DateTime)
    garde = Field(String)
    tickets_ouverts = Field(Integer)
    clotures_rapidement = Field(Integer)
    pourcentage = Field(Float)

    # QB properties
    qbtitle = u'clotures_dans_la_journee'
    qbfilter = {
        'jour' : ALL_DATE_FILTERS,
        'garde': STD_FILTERS,
        'tickets_ouverts' : STD_FILTERS,
        'clotures_rapidement': STD_FILTERS,
        'pourcentage': STD_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

class CloturesDansLaJourneeSemaine(Entity, QBEntity):
    # options
    using_options(tablename = 'clotures_dans_la_journee_week', allowcoloverride=True)

    # fields
    jour = Field(DateTime)
    garde = Field(String)
    tickets_ouverts = Field(Integer)
    clotures_rapidement = Field(Integer)
    pourcentage = Field(Float)

    # QB properties
    qbtitle = u'clotures_dans_la_journee'
    qbfilter = {
        'jour' : ALL_DATE_FILTERS,
        'garde': STD_FILTERS,
        'tickets_ouverts' : STD_FILTERS,
        'clotures_rapidement': STD_FILTERS,
        'pourcentage': STD_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }


class CloturesDansLaJourneeMois(Entity, QBEntity):
    # options
    using_options(tablename = 'clotures_dans_la_journee_month', allowcoloverride=True)

    # fields
    jour = Field(DateTime)
    garde = Field(String)
    tickets_ouverts = Field(Integer)
    clotures_rapidement = Field(Integer)
    pourcentage = Field(Float)

    # QB properties
    qbtitle = u'clotures_dans_la_journee'
    qbfilter = {
        'jour' : ALL_DATE_FILTERS,
        'garde': STD_FILTERS,
        'tickets_ouverts' : STD_FILTERS,
        'clotures_rapidement': STD_FILTERS,
        'pourcentage': STD_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

class RapiditeClotureSiemensOuPas(Entity, QBEntity):
    # options
    using_options(tablename = 'rapidite_cloture_siemens_ou_pas', allowcoloverride=True)

    # fields
    jour = Field(DateTime, colname = 'timestep')
    tickets_ouverts = Field(Integer)
    clotures_rapidement = Field(Integer)
    pourcentage = Field(Float)
    ticket_siemens = Field(Boolean)

    # QB properties
    qbtitle = u'clotures_dans_la_journee'
    qbfilter = {
        'jour' : ALL_DATE_FILTERS,
        'garde': STD_FILTERS,
        'tickets_ouverts' : STD_FILTERS,
        'clotures_rapidement': STD_FILTERS,
        'pourcentage': STD_FILTERS,
        'ticket_siemens': STD_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

class NombreTicketsCloturesOuPas(Entity, QBEntity):
    # options
    using_options(tablename = 'nombre_tickets_fermes_journee', allowcoloverride=True)

    # fields
    jour = Field(DateTime)
    nombre = Field(Integer)
    statut_cloture = Field(Integer)
    incident = Field(Boolean)
    ticket_siemens = Field(Boolean)

    # QB properties
    qbtitle = u'clotures_dans_la_journee'
    qbfilter = {
        'jour' : ALL_DATE_FILTERS,
        'nombre' : STD_FILTERS,
        'statut_cloture': STD_FILTERS,
        'incident' : STD_FILTERS,
        'ticket_siemens' : STD_FILTERS,
        }
    qbgroup_by = {
        }
    qbfield_translations = {
        }

