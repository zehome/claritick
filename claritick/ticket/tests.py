# -*- coding: utf-8 -*-

import datetime
from django.test import TestCase
from django.utils import timezone
from customer.models import Customer
from claritick.models import User
from ticket.models import Ticket, State, Priority


class ClaritickTestCase(TestCase):
    def setUp(self):
        # To be removed by upgrading south (intial_data loading bug django 1.6)
        # e7a3bacad9bd61fd6d7a85b3be930821a05b121f
        State(label="new").save()
        Priority(label="normal").save()
        self.state1 = State.objects.get(pk=1)
        self.priority1 = Priority.objects.get(pk=1)
        self.root_customer = Customer(name="Root", parent=None)
        self.root_customer.save()
        self.branch1 = Customer(name="Branch1", parent=self.root_customer)
        self.branch1.save()
        self.branch2 = Customer(name="Branch2", parent=self.branch1)
        self.branch2.save()
        self.leafb1 = Customer(name="Leafb1", parent=self.branch1)
        self.leafb1.save()
        self.leafb1b2 = Customer(name="Leafb1b2", parent=self.branch2)
        self.leafb1b2.save()
        self.su = User.objects.create_superuser(
            username="root", password="root",
            first_name="root", last_name="root",
            email="root@root.root",
            customer=self.root_customer)
        self.user_b1 = User.objects.create_user(
            username="branch1", password="branch1",
            first_name="branch1", last_name="branch1",
            email="branch1@branch1.com",
            customer=self.branch1)

class TicketTestCase(ClaritickTestCase):
    def setUp(self):
        super(TicketTestCase, self).setUp()
        self.t1 = Ticket(
            state=self.state1, priority=self.priority1,
            customer=self.root_customer,
            title="Root ticket", opened_by=self.su)
        self.t1.save()
        self.t2 = Ticket(
            state=self.state1, priority=self.priority1,
            customer=self.branch1,
            title="Branch1 ticket", opened_by=self.su)
        self.t2.save()
        self.t3 = Ticket(
            state=self.state1, priority=self.priority1,
            customer=self.branch2,
            title="Branch2 ticket", opened_by=self.su)
        self.t3.save()
        self.t4 = Ticket(
            state=self.state1, priority=self.priority1,
            customer=self.leafb1b2,
            title="Leaf b1b2 ticket", opened_by=self.su)
        self.t4.save()

    def test_ticket_all(self):
        qs = Ticket.objects.foruser(self.su)
        self.assertEqual(qs.count(), 4)

    def test_ticket_opened(self):
        self.t1.date_close = timezone.now()
        self.t1.save()
        qs = Ticket.opened.foruser(self.su)
        self.assertEqual(qs.count(), 3)

    def test_ticket_closed(self):
        self.t3.date_close = timezone.now()
        self.t3.save()
        qs = Ticket.closed.foruser(self.su)
        self.assertEqual(qs.count(), 1)

    def test_ticket_date_modification(self):
        d1 = timezone.now() - datetime.timedelta(days=1)
        self.t3.last_modification = d1
        self.assertEqual(self.t3.last_modification, d1)
        self.t3.save()
        self.assertNotEqual(self.t3.last_modification, d1)

    def test_ticket_add_tag(self):
        self.t1.tags.add("admin", "staff")
        self.t1.tags.add("key")
        self.assertEqual(list(self.t1.tags.names()),
                         [u"admin", u"staff", u"key"])
        self.t1.tags.clear()
        self.assertFalse(self.t1.tags.all())