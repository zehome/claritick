import datetime
import time
from sqlalchemy.orm import Query
from django.utils   import simplejson as json

def get_granularity(delta, min, max, just_get_granularity = True, allow_non_sql_granularities = False):
    """
    Finds a granularity that will display a number of points between 'min' and 'max'
    for this timedelta
    """
    # available_granularities = ['second','minute','hour','day','week','month','quarter','year','decade','century','millennium']
    usedays = True
    if isinstance(delta, (int, float)):
        delta = datetime.timedelta(seconds = delta)
    found = False
    available_granularities = [
        ('day'       , 1),
        ('week'      , 7),
        ]
    if allow_non_sql_granularities:
        available_granularities.append(('2weeks'    , 14))
    available_granularities.extend([
        ('month'     , 30),
        ('quarter'   , 4 * 30),
        ('year'      , 360),
        ('decade'    , 3600),
        ('century'   , 36000),
        ('millennium', 360000),
        ])
    actual_point_number = None
    current_granularity_index = current_granularity = None
    while (actual_point_number is None or actual_point_number > max):
        if current_granularity_index is None:
            current_granularity_index = 0
        else:
            current_granularity_index += 1
        current_granularity = available_granularities[current_granularity_index]
        actual_point_number = float(delta.days) / current_granularity[1]
    if actual_point_number > min:
        found = True
    if not found:
        usedays = False
        # Less than a day, compute delta.seconds
        available_granularities = [
            ('second' , 1),
            ('minute' , 60),
            ('hour'   , 60*60),
            ]
        if allow_non_sql_granularities:
            available_granularities.extend([
                ('2weeks'    , 14),
                ('2hour'  , 60*60*2),
                ('6hour'  , 60*60*6),
                ('12hour' , 60*60*12),
                ])
        available_granularities.extend([
            ('day'   , 24*60*60),
            ])
        seconds = delta.seconds + delta.days * 60*60*24
        actual_point_number = None
        current_granularity_index = current_granularity = None
        while (actual_point_number is None or actual_point_number > max):
            if current_granularity_index is None:
                current_granularity_index = 0
            else:
                current_granularity_index += 1
            current_granularity = available_granularities[current_granularity_index]
            actual_point_number = float(seconds) / current_granularity[1]
    if not current_granularity:
        logger.error("Can't comput granularity for delta %s min %s max %s", delta, min, max)
    if just_get_granularity:
        return current_granularity[0]
    granularity_size = current_granularity[1]
    if usedays:
        granularity_size *= 24*60*60
    return current_granularity[0], granularity_size, actual_point_number

def add_granularity_to_date(date, granularity, quantity = 1):
    index, qty = {
        'year' : (0, 1),
        'month': (1, 1),
        'week' : (2, 7),
        'day' : (2, 1),
        'hour' : (3, 1),
        'minute' : (4, 1),
        'second' : (5, 1),
        }.get(granularity, (0,0))
    timetup = list(date.timetuple())
    timetup[index] += (qty * quantity)
    return datetime.datetime.fromtimestamp(time.mktime(timetup), date.tzinfo)

def debug_inline_params(stmt, bind=None):
    """Compiles a query or a statement and inlines bindparams.
    
    WARNING: Does not do any escaping."""
    if isinstance(stmt, Query):
        if bind is None:
            bind = stmt.session.get_bind(stmt._mapper_zero_or_none())
        stmt = stmt.statement
    else:
        if bind is None:
            bind = stmt.bind

    compiler = bind.dialect.statement_compiler(bind.dialect, stmt)
    compiler.bindtemplate = "%%(%(name)s)s"
    compiler.compile()
    def my_custom_repr(stuff):
        if isinstance(stuff, basestring):
            return "'%s'" % (stuff,)
        if isinstance(stuff, datetime.datetime):
            return stuff.strftime("'%Y-%m-%d %H:%M:%S'")
    return compiler.string % dict((k, my_custom_repr(v)) for k,v in compiler.params.items())

NOT_SERIALIZABLE_TYPES = {
    datetime.datetime:
        lambda v: {"custom_type":"datetime","value":list(v.timetuple())[:6]},
    datetime.timedelta:
        lambda v: {"custom_type":"timedelta","value":v.seconds + v.days * 24 * 60 * 60},
    datetime.date:
        lambda v: {"custom_type":"datetime","value":list(v.timetuple())[:6]},
    datetime.time:
        lambda v: str(list(v.timetuple())[:6]),
    }
DESERIALIZE_CUSTOM_TYPES = {
    'timedelta':
        lambda v: datetime.timedelta(seconds = v),
    'datetime':
        lambda v: (datetime.date if len(v) == 3 else datetime.datetime)(*v),
    }
def serializable_list(source_list):
    """
    Rend une liste JSON serializable (en convertissant les types non serializables en chaines)
    Recursif
    """
    result = []
    for v in source_list:
        for ktype, vlambda in NOT_SERIALIZABLE_TYPES.items():
            if isinstance(v, ktype):
                v = vlambda(v)
                break
        if isinstance(v, dict):
            v = serializable_dict(v)
        if isinstance(v, (tuple, list)):
            v = serializable_list(v)
        result.append(v)
    return result

def serializable_dict(source_dict):
    """
    Rend un dictionnaire JSON serializable (en convertissant les types non serializables en chaines)
    Recursif
    """
    result={}
    for k, v in source_dict.items():
        for ktype, vlambda in NOT_SERIALIZABLE_TYPES.items():
            if isinstance(v, ktype):
                v = vlambda(v)
                break
        if isinstance(v, dict):
            v = serializable_dict(v)
        if isinstance(v, (tuple, list)):
            v = serializable_list(v)
        result[k] = v
    return result

def jsondump(v):
    for ktype, vlambda in NOT_SERIALIZABLE_TYPES.items():
        if isinstance(v, ktype):
            v = vlambda(v)
            break
    if isinstance(v, dict):
        v = serializable_dict(v)
    if isinstance(v, (tuple, list)):
        v = serializable_list(v)
    return json.dumps(v)

def deserialize_custom(value):
    if isinstance(value, dict):
        return deserialize_custom_dict(value)
    if isinstance(value, (tuple, list)):
        return deserialize_custom_list(value)
    return value

def deserialize_custom_dict(source_dict):
    if 'custom_type' in source_dict and source_dict['custom_type'] in DESERIALIZE_CUSTOM_TYPES and 'value' in source_dict:
        return DESERIALIZE_CUSTOM_TYPES[source_dict['custom_type']](source_dict['value'])
    for key, value in source_dict.iteritems():
        source_dict[key] = deserialize_custom(value)
    return source_dict

def deserialize_custom_list(source_list):
    result = []
    for item in source_list:
        result.append(deserialize_custom(item))
    return result

def jsonload(v):
    """
    Json Load that convert the 'custom types' back to python types
    """
    result = json.loads(v)
    for key, value in result.iteritems():
        result[key] = deserialize_custom(value)
    return result
