#
# A sample model declaration for the demonstration of Query Builder
#
# In order to use Query Builder with your own database, you need to
# define your models as in this sample. (Create a folder named by
# you application or copy the sample folder).

from qbuilder.sample.models import Product, ProductCategory, Customer, OrderingHistory
QBSelectables = ['Product', 'Customer', 'Ordering', ] # The model that are directly available to the user
QBEventsConfig = {
    'model' : 'OrderingHistory',
    'partition_field' : 'id_ordering',
    'event_type' : 'event_type',
    'event_date' : 'event_date',
    }
