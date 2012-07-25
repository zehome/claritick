from qbuilder.models import QBEntity
from elixir import Entity, using_options, using_table_options, Field, Integer, String, Float, DateTime, ManyToOne

class ProductCategory(Entity, QBEntity):
    using_options(tablename = 'product_category')
    using_table_options(schema = 'qbuilder')

    # Declare only the fields you want to query
    # name your primary key 'pk'
    pk = Field(Integer, primary_key = True, colname = 'id_product_category')
    name = Field(String)

    # Here you declare how Query Builder should handle this model :
    qbtitle = u'product category'
    qbfilter = {
        'name' : ('=', 'IN', '!='),
        }
    qbgroup_by = {
        'name':'name',
        }
    # Pour Debug a enlever
    def __str__(self):
        return "name: %s%s" % (self.name, "\n")

class Product(Entity, QBEntity):
    using_options(tablename = 'product')
    using_table_options(schema = 'qbuilder')

    # Declare only the fields you want to query
    # name your primary key 'pk'
    pk = Field(Integer, primary_key = True, colname = 'id_product')
    name = Field(String)
    base_price = Field(Float)
    category = ManyToOne('ProductCategory', colname = 'id_product_category', target_column = 'id_product_category')

    # Here you declare how Query Builder should handle this model :
    qbtitle = u'product'
    qbfilter = {
        'name' : ('=', 'IN', '!='),
        'base_price' : ('gt', 'lt', 'gte', 'lte'),
        }
    qbfield_translations = {
        'base_price': u'base price',
        }
    qbforeigns = {
        'ProductCategory' : [],
        }
    # Pour Debug a enlever
    def __str__(self):
        return "name: %s, base_price: %f%s" % (self.name, self.base_price, "\n")

class Customer(Entity, QBEntity):
    using_options(tablename = 'customer')
    using_table_options(schema = 'qbuilder')

    # Declare only the fields you want to query
    # name your primary key 'pk'
    pk = Field(Integer, primary_key = True, colname = 'id_customer')
    name = Field(String)
    discount = Field(Float)

    # Here you declare how Query Builder should handle this model :
    qbtitle = u'customer'
    qbfilter = {
        'name' : ('=', 'IN', '!='),
        'discount' : ('gt', 'lt', 'gte', 'lte'),
        }
    # Pour Debug a enlever
    def __str__(self):
        return "name: %s, discount: %f%s" % (self.name, self.discount, "\n")

class Ordering(Entity, QBEntity):
    using_options(tablename = 'ordering')
    using_table_options(schema = 'qbuilder')

    pk = Field(Integer, primary_key = True, colname = 'id_ordering')
    create_date = Field(DateTime)
    payment_date = Field(DateTime)
    shipment_date = Field(DateTime)
    status = Field(Integer)
    customer = ManyToOne('Customer', colname = 'id_customer', target_column = 'id_customer')

    qbdate_criteria = 'create_date'
    qbfilter = {
        'create_date' : (
            'date_gt',
            'date_lt',
            'date_x_last_n',
            'date_hour_gt',
            'date_hour_lt',
            'date_hour_eq',
            'date_hour_ne',
            'date_month_gt',
            'date_month_lt',
            'date_month_eq',
            'date_month_ne',
            'date_gt_now_less',
            'date_lt_now_less',
            ),
        'status' : (
            '=',
            'IN',
            '!='
            ),
        }
    qbforeigns = {
        'Customer' : [],
        }
    # Pour Debug, a enlever
    def __str__(self):
        return "create_date: %s, payment_date: %s, shipment_date: %s, status: %d%s" % (self.create_date, self.payment_date, self.shipment_date, self.status, "\n")

class ProductOrdering(Entity, QBEntity):
    using_options(tablename = 'product_ordering')
    using_table_options(schema = 'qbuilder')

    pk = Field(Integer, primary_key = True, colname = 'id_product_ordering')
    price = Field(Float)
    ordering = ManyToOne('Ordering', colname = 'id_ordering', target_column = 'id_ordering')
    product = ManyToOne('Product', colname = 'id_product', target_column = 'id_product')

    qbforeigns = {
        'Ordering' : [],
        'Product' : [],
        }
    # Pour Debug, a enlever
    def __str__(self):
        return "price: %d%s" % (self.price, "\n")

class OrderingHistory(Entity, QBEntity):
    using_options(tablename = 'ordering_history')
    using_table_options(schema = 'qbuilder')

    pk = Field(Integer, primary_key = True, colname = 'id_ordering_history')
    ordering = ManyToOne('Ordering', colname = 'id_ordering', target_column = 'id_ordering')
    event_type = Field(Integer)
    event_date = Field(DateTime)

    qbforeigns = {
        'Ordering' : [],
        }
    qbfilter = {
        'event_type' : ('=', 'IN', '!=', '>', '>=', '<', '<='),
        'event_date' : (
            'date_gt',
            'date_lt',
            'date_x_last_n',
            'date_hour_gt',
            'date_hour_lt',
            'date_hour_eq',
            'date_hour_ne',
            'date_month_gt',
            'date_month_lt',
            'date_month_eq',
            'date_month_ne',
            'date_gt_now_less',
            'date_lt_now_less',
            ),
        }
    # Pour Debug, a enlever
    def __str__(self):
        return "event_type: %d, event_date: %s%s" % (self.event_type, self.event_date, "\n")

__all__ = [ProductCategory, Product, Customer, Ordering, ProductOrdering, OrderingHistory]
