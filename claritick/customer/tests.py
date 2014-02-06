# -*- coding: utf-8 -*-

from django.test import TestCase
from customer.models import Customer
from claritick.models import User


class CustomerTestCase(TestCase):
    def setUp(self):
        self.root_customer = Customer(name="Root", parent=None)
        self.root_customer.save()
        self.branch1 = Customer(name="Branch1", parent=self.root_customer)
        self.branch1.save()
        self.leaf1 = Customer(name="Leaf1", parent=self.root_customer)
        self.leaf1.save()
        self.branch2 = Customer(name="Branch2", parent=self.branch1)
        self.branch2.save()
        self.Leafb1 = Customer(name="Leafb1", parent=self.branch1)
        self.Leafb1.save()
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

    def test_get_descendants(self):
        qs = self.root_customer.get_descendants(include_self=True)
        names = [c.name for c in qs]
        self.assertEqual(qs.count(), 6)
        # Test name ordering
        self.assertEqual(names, ["Root", "Branch1", "Branch2",
            "Leafb1b2", "Leafb1", "Leaf1"])

    def test_tree_modify(self):
        self.leaf1.move_to(self.branch1)
        qs = self.branch1.get_children()
        self.assertEqual(qs.count(), 3, [c.name for c in qs])
        self.assertEqual([c.name for c in qs], ["Branch2", "Leafb1", "Leaf1"])

    def test_user_visibility(self):
        """
        The user visibility map should be cached
        """