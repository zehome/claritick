# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template                import RequestContext
from django.conf import settings

from django.utils   import simplejson as json
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django import forms

from qbuilder.main import QBuilder
from qbuilder.models import QueryParameters, QueryResult
from qbuilder.lib import jsondump, jsonload
from qbuilder.constants import QB_STYPE_NAMES, QB_FRISE_COLORS

import logging
import datetime

logger = logging.getLogger("qbuilder")

# MAIN VIEWS
def home(request):
    context = RequestContext(request)
    context["queries"] = QueryParameters.objects.filter(status__gt = -50).order_by('pk')
    return make_response("base.html", context)

def create(request):
    context = RequestContext(request)
    context.update({
        })
    return make_response("create.html", context)

def edit(request, query_id):
    context = RequestContext(request)
    # Load the query
    try:
        query_param = QueryParameters.objects.get(pk = query_id)
        jsondata = json.loads(query_param.data)
    except QueryParameters.DoesNotExist:
        return make_response("error.html", {"message" : _(u"No query with id %s") % (query_id,)})
    except ValueError:
        return make_response("error.html", {"message" : _(u"Incorrect parameters for query %s") % (query_id,)})
    # First, commit the edits if any:
    if request.method == "POST":
        for k, v in request.POST.iteritems():
            if k == 'new_parameter_name' and v:
                jsondata.update({v:request.POST.get('new_parameter_value','')})
                continue
            if k == "new_parameter_value": # On n'enregistre pas ce parametre dans data
                continue
            if '^' in v:
                v = v.split('^')
            updating_dict = {}
            jsondata.update({k:v})
        # Commit this to the BDD
        query_param.data = json.dumps(jsondata)
        QueryResult.objects.filter(query__pk = query_id).delete()
        query_param.save()
    # For each param of the query, build a form field
    form_fields = SortedDict()
    filter_parameters = {}
    grouping_parameters = {}
    # Start by taking only the "non filter" and "non grouping" fields
    # On this first pass, we also put filters and groupings in a custom hashing
    for k, v in jsondata.iteritems():
        index = k.split('_')[-1]
        if k.startswith('model_for_filter') or\
             k.startswith('field_for_filter') or\
             k.startswith('type_for_filter'):
            filter_parameters.setdefault(int(index), {}).update({k:v})
        elif k.startswith('value_for_filter'):
            if index.endswith('[]'):
                index = index[:-2]
            filter_parameters.setdefault(int(index), {}).update({k:v})
        elif k.startswith('model_for_grouping') or\
             k.startswith('field_for_grouping') or\
             k.startswith('type_for_grouping'):
            grouping_parameters.setdefault(0, {}).update({k:v})
        elif k.startswith('value_for_grouping'):
            if index.endswith('[]'):
                index = index[:-2]
            grouping_parameters.setdefault(int(index), {}).update({k:v})
        else:
            if isinstance(v, (list, tuple)):
                v = '^'.join([unicode(x) for x in v])
            form_fields[k] = forms.CharField(initial = v)
    # Then filters
    filters = filter_parameters.keys()
    filters.sort()
    for i in filters:
        form_fields['model_for_filter_%d' % (i,)] = forms.CharField(initial = filter_parameters[i]['model_for_filter_%d' % (i,)])
        form_fields['field_for_filter_%d' % (i,)] = forms.CharField(initial = filter_parameters[i].get('field_for_filter_%d' % (i,), ''))
        form_fields['type_for_filter_%d' % (i,)] = forms.CharField(initial = filter_parameters[i].get('type_for_filter_%d' % (i,), ''))
        if 'value_for_filter_%d[]' % (i,) in filter_parameters[i]:
            form_fields['value_for_filter_%d[]' % (i,)] = forms.CharField(initial = '^'.join(filter_parameters[i]['value_for_filter_%d[]' % (i,)]))
        else:
            form_fields['value_for_filter_%d' % (i,)] = forms.CharField(initial = filter_parameters[i].get('value_for_filter_%d' % (i,), ''))
    # And finally groupings
    groupings = grouping_parameters.keys()
    groupings.sort()
    for i in groupings:
        form_fields['model_for_grouping_%d' % (i,)] = forms.CharField(initial = grouping_parameters[i]['model_for_grouping_%d' % (i,)])
        form_fields['field_for_grouping_%d' % (i,)] = forms.CharField(initial = grouping_parameters[i].get('field_for_grouping_%d' % (i,), ''))
        if 'type_for_grouping_%d' % (i,) in grouping_parameters[i]:
            form_fields['type_for_grouping_%d' % (i,)] = forms.CharField(initial = grouping_parameters[i]['type_for_grouping_%d' % (i,)])
            if 'value_for_grouping_%d[]' % (i,) in grouping_parameters[i]:
                form_fields['value_for_grouping_%d[]' % (i,)] = forms.CharField(initial = '^'.join(grouping_parameters[i]['value_for_grouping_%d[]' % (i,)]))
            else:
                form_fields['value_for_grouping_%d' % (i,)] = forms.CharField(initial = grouping_parameters[i].get('value_for_grouping_%d' % (i,), ''))
    # Add an empty "free" field
    form_fields["new_parameter_name"] = forms.CharField(label = _(u"New parameter : name"))
    form_fields["new_parameter_value"] = forms.CharField(label = _(u"New parameter : value"))
    # Create a dynamic form class
    formclass = type("EditQbuilderQuery", (forms.Form,), form_fields)
    # Use this form
    context["form"] = formclass()
    context["query"] = query_param
    return make_response("edit.html", context)

# "Query Builder" VIEWS
def prepare_charts(graph_data, query_id):
    templates = ['pie', 'bar', 'area', 'line', 'column', 'scatter', 'series', 'stackedbar', 'stackedcolumn', 'frise']
    try:
        query_param = QueryParameters.objects.get(pk = query_id)
        jsondata = json.loads(query_param.data)
    except QueryParameters.DoesNotExist:
        return make_response("error.html", {"message" : _(u"No query with id %s") % (query_id,)})
    except ValueError:
        return make_response("error.html", {"message" : _(u"Incorrect parameters for query %s") % (query_id,)})
    graph_type = jsondata.get("graph_type", "line")
    if graph_type not in templates:
        return make_response("error.html", {"message" : _(u"No templates with id %s") % (query_id,)})
    # On regarde si on a déjà des data pour cette requête
    logger.debug("Reading cache")
    cached_result = QueryResult.objects.filter(query = query_param).order_by('-date')
    if cached_result.count() != 0 and graph_data.get("cache_allowed", False):
        logger.debug("Using cached results")
        cached_result = cached_result[0]
        graph_data["subtitle_suffix"] = _(u"Using cached results generated on %s") % (cached_result.date.strftime("%d/%m %H:%M"),)
        graph_data.update(jsonload(cached_result.data))
    else:
        graph_data.update(get_context(jsondata = jsondata))
    entetes_colonnes = []
    subtitle = ""
    if "statistics" in jsondata:
        logger.debug("Convert statistics to highcharts")
        dataHC = qbuilder_stats_to_highcharts(graph_data["statistics"], graph_type, jsondata.get("statistics",[]))
        if graph_data["query_result"]:
            entetes_colonnes = graph_data["keys"]
            stats_on = entetes_colonnes[1]
            subtitle = _("Statistics by %s") % (stats_on)
    elif graph_type == 'frise':
        logger.debug("Convert data to 'frise'")
        dataHC = qbuilder_temps_rendu_to_frise_tat(graph_data["query_result"], jsondata, graph_type, 1, 0)
    else:
        logger.debug("Select the right type of data conversion for highcharts")
        dataHC = select_function_qbuilder_data_to_highcharts(graph_data["query_result"], graph_type, 1, 0)
        if graph_data["query_result"]:
            entetes_colonnes = graph_data["keys"]
            subtitle = make_Z(entetes_colonnes)
            if subtitle:
                subtitle = _(u"Grouped by : %s") % (subtitle,)
    logger.debug("Building graph parameters")
    data_param = init_data_param(graph_type, jsondata, dataHC)
    graph_data.update(data_param)
    if graph_data.get("subtitle_suffix") and subtitle:
        graph_data["subtitle_suffix"] = u" - " + graph_data["subtitle_suffix"]

    if graph_type == 'frise':
        graph_data.update({
            "title_text": query_param.name,
            "subtitle_text": subtitle,
            "description": jsondata.get("description"),
            })
        graph_data.update(dataHC)
    else:
        # Traduction des libelles de la legende
        if jsondata.get("graph_type") == "pie":
            for d in dataHC["xValues"]:
                for x in d["data"]:
                    x["name"] = jsondata.get("label_for_%s" % x["name"], x["name"])
        else:
            for x in dataHC["xValues"]:
                x["name"] = jsondata.get("label_for_%s" % x["name"], x["name"])

        yAxis_title_text = jsondata.get("label_for_%s" % entetes_colonnes[0], entetes_colonnes[0]) if entetes_colonnes else None
        xAxis_title_text = jsondata.get("label_for_%s" % entetes_colonnes[1], entetes_colonnes[1]) if entetes_colonnes else None
        if 'statistics' in jsondata:
            xAxis_title_text = jsondata.get("label_for_%s" % entetes_colonnes[2], entetes_colonnes[2]) if entetes_colonnes else None

        xAxis_labels_rotation = 0
        if len(dataHC["xLabels"]) > 10: # A RENDRE PARAMETRABLE
            xAxis_labels_rotation = -90 # A RENDRE PARAMETRABLE (-90 ou -45)
        graph_data.update(
            {
            "title_text": query_param.name,
            "subtitle_text": subtitle,
            "xAxis_categories": jsondump([jsondata.get("label_for_%s" % x, x) for x in dataHC["xLabels"]]),
            "yAxis_title_text": yAxis_title_text,                # A RENDRE PARAMETRABLE
            "xAxis_title_text": xAxis_title_text,                # A RENDRE PARAMETRABLE
            "xAxis_labels_rotation": xAxis_labels_rotation,  
            "seriesData": jsondump(dataHC["xValues"]),
            "description": jsondata.get("description"),
            }
        )
    return graph_data

def views_highcharts(request, query_ids):
    liste_id = query_ids.split(',')
    context = RequestContext(request)
    context["queries"] = QueryParameters.objects.filter(status__gt = -50).order_by('pk')
    context["show_data"] = request.GET.get("show_data", "0") == "1"
    context["show_sql"] = request.GET.get("show_sql", "0") == "1"
    context["full_screen"] = request.GET.get("full_screen", "0") == "1"
    context["cache_allowed"] = request.GET.get("no_cache", "0") != "1"
    context.update({
        "graphs_data" : [],
        })

    # TODO : multi-graphe
    prepare_charts(context, liste_id[0])

    return make_response("base.html", context)

def vue_test(request):  # VUE TEST
    context = RequestContext(request)
    context.update(get_context())
    return make_response('vue_test.html',
            {
            },
            context_instance = context)

# HELPERS
def get_context(jsonfilename = None, jsondata = None):
    context= {}
    qb = QBuilder(logger, make_db_url())
    qb.loadmodels(getattr(settings, 'QBUILDER_MODELS_NAME', 'claritick'))
    if jsonfilename:
        qb.loadjson(jsonfilename)
    if jsondata:
        qb.query_parameters = jsondata
    if jsonfilename or jsondata:
        logger.debug("Running Query")
        all_data = qb.all_data()
        context.update({
            "query_result": all_data,
            "sql_query":    str(qb.query),
            })
        if "statistics" in jsondata:
            logger.debug("Running Statistics")
            context["statistics"] = qb.statistics(jsondata.get("percentile", 100), True)
        if context["query_result"]:
            context["keys"] = context["query_result"][0].keys()
    return context

def make_db_url():
    """
    Takes the django settings and returns a db url of this form:

    If a 'qbuilder' db exists, use this one else, use the 'default' one
    """
    DEFAULT_QB_DB_SETTINGS = {
                             'HOST': getattr(settings, 'DATABASE_HOST', '127.0.0.1'),
                             'NAME': getattr(settings, 'DATABASE_NAME', 'qbuilder'),
                             'PASSWORD': getattr(settings, 'DATABASE_PASSWORD', 'qbuilder'),
                             'PORT': getattr(settings, 'DATABASE_PORT', ''),
                             'USER': getattr(settings, 'DATABASE_USER', 'qbuilder'),
                             }
    db_settings = getattr(settings, 'DATABASES', {'qbuilder':DEFAULT_QB_DB_SETTINGS})
    db_settings = db_settings.get('qbuilder', db_settings.get('default', DEFAULT_QB_DB_SETTINGS))
    if not db_settings['PORT']:
        db_settings['PORT'] = '5432'
    return "postgresql+psycopg2://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s" % db_settings

def make_response(template, context, **kwargs):
    return render_to_response('qbuilder/%s' % (template,), context, **kwargs)

def init_data_param(graph_type, jsondata = {}, data = []):
    data_param = {
        "yAxis_title_align": "middle",
        "yAxis_stackLabels": "false",
        "tooltip_formatter": "this.y",
        "plotOptions": jsondump({}),
        "yAxis": {
            "min": None,
            "max": None,
            },
        "xAxis": {}
        }
    tooltip_this_x = 'this.x';
    tooltip_this_y = 'this.y';
    python_type_to_js_converter_function = {
        datetime.datetime:
            lambda v: "dojo.date.locale.format(new Date(%s))" % (v,),
        datetime.timedelta:
            lambda v: """mca.timestampdisplay(%s, "S", 3)""" % (v,),
        }
    if isinstance(data, dict) and 'xType' in data:
        tooltip_this_x = python_type_to_js_converter_function.get(type(data['xType']), lambda v: v)(tooltip_this_x)
    if isinstance(data, dict) and 'yType' in data:
        tooltip_this_y = python_type_to_js_converter_function.get(type(data['yType']), lambda v: v)(tooltip_this_y)
    if graph_type == "area":
        data_param["tooltip_formatter"] = "''+ this.series.name +': '+ " + tooltip_this_y
        data_param["plotOptions"] = jsondump({"area": {"fillOpacity": 0.9},})
    elif graph_type == "bar":
        data_param["yAxis_title_align"] = "high"
        data_param["tooltip_formatter"] = "''+ this.series.name +': '+ " + tooltip_this_y
        data_param["plotOptions"] = jsondump({"bar": {"dataLabels":{"enabled":True},},})
    elif graph_type == "column":
        data_param["tooltip_formatter"] = "''+ this.series.name +': '+ " + tooltip_this_y
        data_param["plotOptions"] = jsondump({"column": {"dataLabels":{"enabled":True},},})
    elif graph_type == "stackedbar":
        data_param["yAxis_title_align"] = "high"
        data_param["tooltip_formatter"] = "''+ this.series.name +': '+ " + tooltip_this_y
        data_param["plotOptions"] = jsondump({"series": {"stacking": "normal"}, "bar": {"dataLabels": {"enabled":True, "color": "#FFFFFF", "align": "center"},},})
    elif graph_type == "stackedcolumn":
        data_param["yAxis_stackedLabels"] = "true"
        data_param["tooltip_formatter"] = "'<b>'+ " + tooltip_this_x + " +'</b><br/>'+ this.series.name +': '+ " + tooltip_this_y + " +'<br/>'"
        if jsondata.get('stacking', 'normal') == 'percent':
            data_param["tooltip_formatter"] = "'<b>'+ " + tooltip_this_x + " +'</b><br/>'+ this.series.name +': '+ Math.round(this.percentage*100)/100 +'%<br/>(' + " + tooltip_this_y + " + ')'"
        data_param["plotOptions"] = jsondump({"column": {"stacking": jsondata.get("stacking", "normal"), "dataLabels": {"enabled": jsondata.get("dataLabels", "1") != "off", "color": "#FFFFFF", "align": "center"},},})
    elif graph_type == "pie":
        data_param["tooltip_formatter"] = "'<b>'+ this.point.name +'</b>: '+ " + tooltip_this_y
        data_param["plotOptions"] = jsondump({"pie": {"size": 280, "allowPointSelect": True, "cursor": "pointer"},})
    elif graph_type == "line":
        data_param["tooltip_formatter"] = "'<b>'+ this.series.name +'</b><br/>'+ " + tooltip_this_x + " +': '+ " + tooltip_this_y
    elif graph_type == "scatter":
        data_param["tooltip_formatter"] = "'<b>'+ this.series.name +'</b><br/>'+Highcharts.dateFormat('%e. %b', " + tooltip_this_x + ") +': '+ " + tooltip_this_y
        data_param["plotOptions"] = jsondump({"scatter": {"marker":{"radius":3},},})
    for key, value in jsondata.items():
        for axis in ('x', 'y'):
            if key.startswith(axis + 'Axis_'):
                real_key = '_'.join(key.split('_')[1:])
                data_param[axis  + 'Axis'][real_key] = convert_input_values_to_HC(value, real_key)
    for axis in ('x', 'y'):
        data_param[axis + 'Axis'] = jsondump(data_param[axis + 'Axis'])
    return data_param

def make_Z(line, x_index = 1, y_index = 0):
    tmp_line = list(line)
    tmp_line.pop(max(x_index, y_index))
    tmp_line.pop(min(x_index, y_index))
    return u" ".join([unicode(cellule) for cellule in tmp_line])

def empty_or_null(data):
    if not data or data is None:
        return u'\u2205' # 2205 : ∅ : Ensemble vide
    return data

def select_function_qbuilder_data_to_highcharts(data, graph_type, x_index = 1, y_index = 0):
    if graph_type == "pie":
        logger.debug("Choosen the pie type")
        return {
            'xLabels' : [],
            'xValues' : [qbuilder_data_pie(data, x_index, y_index),],
            }
    elif len(data) == 0:
        logger.debug("Choosen the no data type")
        return {
            "xLabels": [],
            "xValues": [],
            }
    else:
        test_data = data[0][x_index]
        if isinstance(test_data, dict) and test_data.get("custom_type","") in ("datetime","timedelta"):
            logger.debug("Choosen the xy type")
            return qbuilder_data_xy(data, graph_type, x_index, y_index)
        elif isinstance(test_data, (int, float, datetime.datetime, datetime.timedelta)):  # A MODIFIER OU A COMPLETER
            logger.debug("Choosen the xy type")
            return qbuilder_data_xy(data, graph_type, x_index, y_index)
        else:
            logger.debug("Choosen the y with xlabels type")
            return qbuilder_data_y_with_xlabels(data, graph_type, x_index, y_index)

def qbuilder_stats_to_highcharts(data, graph_type, stat_types = []):
    keys = data.keys()
    dataHC = {
        "xLabels": keys, #[u" ".join([str(subk) for subk in k]) for k in keys],
        "xValues": [],
        "xType": keys[0],
        "yType": data.values()[0].values()[0],
        }
    for serie in stat_types:
        seriedata = []
        for key in keys:
            if serie in data[key]:
                seriedata.append(data[key][serie])
                dataHC['xType'] = key
        if seriedata:
            dataHC["xValues"].append({
                "type": graph_type,
                "name" : _(QB_STYPE_NAMES[serie]),
                "data" : seriedata,
                })
    return dataHC

def qbuilder_data_pie(data, x_index = 1, y_index = 0):
    dataPie = {"type": "pie", "data":[],}
    for line in data:
        dataPie["data"].append({
            "name": line[x_index],
            "y": line[y_index],
            "sliced": False,
            "selected": False,
            })
    return dataPie

def qbuilder_data_xy(data, graph_type, x_index = 1, y_index = 0):
    dataHC = {
        "xLabels": [],
        "xValues": [],
        "xType": data[0][x_index],
        "yType": data[0][y_index],
        }
    keysZ = []
    for line in data:
        z = make_Z(line, x_index)
        if z not in keysZ:
            keysZ.append(z)
    for z in keysZ:
        dataHC["xValues"].append({
            "type": graph_type,
            "name": z,
            "data": [(line[x_index], line[y_index]) for line in data if make_Z(line, x_index, y_index) == z],
            })
    return dataHC

def qbuilder_data_y_with_xlabels(data, graph_type, x_index = 1, y_index = 0):
    dataHC = {
        "xLabels": [],
        "xValues": [],
        "xType": data[0][x_index],
        "yType": data[0][y_index],
        }
    keysZ = []
    for line in data:
        xlabel = empty_or_null(line[x_index])
        if xlabel not in dataHC['xLabels']:
            dataHC['xLabels'].append(xlabel)
        z = make_Z(line, x_index)
        if z not in keysZ:
            keysZ.append(z)
    for z in keysZ:
        dataHC["xValues"].append({
            "type": graph_type,    
            "name": empty_or_null(z),
            "data": [line[y_index] for line in data if make_Z(line, x_index) == z],
            })
    return dataHC

def convert_input_values_to_HC(value, key):
    if value == 'false':
        return False
    return value
