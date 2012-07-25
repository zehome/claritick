import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import sample.models
from elixir import *
from optparse import OptionParser

from random import randrange
import random
from datetime import timedelta, datetime

class FDBException(Exception):
    pass

class FDBMsgException(FDBException):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class FDBInvalidType(FDBMsgException):
    pass

class FDBQty(FDBMsgException):
    pass

CREATION_PAYMENT_MAX_DELTA = 5
PAYMENT_SHIPPING_MAX_DELTA = 3

def random_date(start_dt, end_dt):
    delta = end_dt - start_dt
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_seconds = randrange(int_delta)
    return (start_dt + timedelta(seconds = random_seconds))

def create_data_ordering(st, start_seed = "1-1-2011 00:00", end_seed = "12-31-2011 23:59"):
    start_dt = datetime.strptime(start_seed, "%m-%d-%Y %H:%M")
    end_dt = datetime.strptime(end_seed, "%m-%d-%Y %H:%M")
    create_dt = payment_dt = shipment_dt = None
    if st >= 0:
        create_dt = random_date(start_dt, end_dt)
    if st >= 1:
        payment_dt = random_date(create_dt, create_dt + timedelta(seconds = randrange(60*60*24*CREATION_PAYMENT_MAX_DELTA)))
    if st >= 2:
        shipment_dt = random_date(payment_dt, payment_dt + timedelta(seconds = randrange(60*60*24*PAYMENT_SHIPPING_MAX_DELTA)))
    customers = sample.models.Customer.query.all()
    current_customer = random.choice(customers)
    return create_dt, payment_dt, shipment_dt, current_customer

def get_prod():
    products = sample.models.Product.query.all()
    current_prod = random.choice(products)
    return current_prod

def check_options(options):
    if options.quantity == False:
        qty_data = 20
    else:
        try:
            qty_data = int(options.quantity)
            if qty_data <= 0:
                raise FDBQty("The value of the amount must be greater than zero")
        except ValueError:
            raise FDBInvalidType("Invalid type parameter")
    if options.product == False:
        max_products = 10
    else:
        try:
            max_products = int(options.product)
            if max_products <= 0:
                raise FDBProd("The value of the production must be greater than zero")
        except ValueError:
            raise FDBInvalidType("Invalid type parameter")
    return qty_data, max_products

def fill_db(options, args):
    qty_data, max_products = check_options(options)
    index = 0
    while index < qty_data:
        st = randrange(3)
        create_dt, payment_dt, shipment_dt, current_customer = create_data_ordering(st)
        current_prod = get_prod()
        current_ordering = sample.models.Ordering(create_date=create_dt, payment_date=payment_dt, shipment_date=shipment_dt, status=st, customer=current_customer)
        sample.models.ProductOrdering(price=(current_prod.base_price * current_customer.discount), ordering=current_ordering, product=current_prod)
        for prod in range(randrange(2, max_products)):
            current_prod = get_prod()
            sample.models.ProductOrdering(price=(current_prod.base_price * current_customer.discount), ordering=current_ordering, product=current_prod)
        event = sample.models.OrderingHistory(ordering=current_ordering, event_type=0, event_date=current_ordering.create_date)
        index2 = 0
        while index2 < prod:
            if st > 0:
                event_rand = randrange(1, 4)
                dt_event = random_date(current_ordering.create_date, current_ordering.payment_date)
            else:
                event_rand = randrange(1, 3)
                dt_event = random_date(current_ordering.create_date, current_ordering.create_date + timedelta(seconds = randrange(60*60*24*CREATION_PAYMENT_MAX_DELTA)))
            if index2 == 0:
                event_rand = 1
            if event_rand == 1:
                index2 += 1
            event = sample.models.OrderingHistory(ordering=current_ordering, event_type=event_rand, event_date=dt_event)
        if st == 1:
            event = sample.models.OrderingHistory(ordering=current_ordering, event_type=3, event_date=current_ordering.payment_date)
        elif st == 2:
            event = sample.models.OrderingHistory(ordering=current_ordering, event_type=3, event_date=current_ordering.payment_date)
            event = sample.models.OrderingHistory(ordering=current_ordering, event_type=4, event_date=current_ordering.shipment_date)
        index += 1
    if options.commit == True:
        session.commit()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-q", "--quantity",
                      dest="quantity", default=False,
                      help="[A TRADUIRE]: Nombre de donnees demander")
    parser.add_option("-p", "--product",
                      dest="product", default=False,
                      help="[A TRADUIRE]: Nombre maximum d'ajout par commande")
    parser.add_option("-c", "--commit",
                      action="store_true", dest="commit", default=False,
                      help="[A TRADUIRE]: Commit la base de donnees generee, (pour commiter suffit d'activer l'option)")
    (options, args) = parser.parse_args()

    metadata.bind = "postgresql+psycopg2://auto:auto@bingo/qbuilder"
    metadata.echo = True
    setup_all()
    fill_db(options, args)
