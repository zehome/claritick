# -*- coding: utf-8 -*-

from django.test import TestCase
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
        self.leaf1 = Customer(name="Leaf1", parent=self.root_customer)
        self.leaf1.save()
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


class CustomerTestCase(ClaritickTestCase):
    def test_get_descendants(self):
        qs = self.su.get_visible_customers()
        names = [c.name for c in qs]
        self.assertEqual(qs.count(), 6)
        # Test name ordering
        self.assertEqual(
            names,
            ["Root", "Branch1", "Branch2", "Leafb1b2", "Leafb1", "Leaf1"])

    def test_tree_modify(self):
        self.leaf1.move_to(self.branch1)
        qs = self.branch1.get_children()
        self.assertEqual(qs.count(), 3, [c.name for c in qs])
        self.assertEqual([c.name for c in qs], ["Branch2", "Leafb1", "Leaf1"])


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
            customer=self.leaf1,
            title="Leaf1 ticket", opened_by=self.su)
        self.t2.save()
        self.t3 = Ticket(
            state=self.state1, priority=self.priority1,
            customer=self.leafb1b2,
            title="LeafB1B2 ticket", opened_by=self.su)
        self.t3.save()
        self.t4 = Ticket(
            state=self.state1, priority=self.priority1,
            customer=self.branch2,
            title="branch2 ticket", opened_by=self.su)
        self.t4.save()

    def test_ticketmanager_foruser_b1(self):
        """
        The user visibility map should be cached
        """
        qs = Ticket.objects.foruser(self.user_b1)
        self.assertEqual(qs.count(), 2, [t.customer for t in qs])

    def test_tickermanager_foruser_su(self):
        qs = Ticket.objects.foruser(self.su)
        self.assertEqual(qs.count(), 4)
