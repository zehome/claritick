# -*- coding: utf-8 -*-

import datetime
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from claritick.models import User
from ticket.models import Ticket, State, Priority
from customer.models import Customer


class EmptyCacheAPITestCase(APITestCase):
    def tearDown(self):
        cache.clear()


class BasicTestCase(object):
    def _test_login(self, username, shouldpass=True, **kwargs):
        data = {"username": username,
                "password": kwargs.get("password", username)}
        url = reverse("api-login")
        response = self.client.post(url, data)
        if shouldpass:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertDictContainsSubset({'isLogged': True}, response.data)
            self.assertDictContainsSubset({
                'username': unicode(username),
            }, response.data["user"])
            self.client.credentials(
                HTTP_X_SESSION_ID=response.data["sessionid"])
        return response


class LoginTestCase(EmptyCacheAPITestCase, BasicTestCase):
    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.customer = Customer(name="root")
        self.customer.save()
        self.su = User.objects.create_superuser(
            username="root", password="root", email="root@email.fr",
            first_name="root", last_name="root",
            customer=self.customer)
        self.nobody = User.objects.create_user(
            username="nobody", password="nobody",  email="nobody@email.fr",
            first_name="firstname", last_name="lastname",
            customer=self.customer)
        self.inactive = User.objects.create_user(
            username="inactive", password="inactive", email="inactive@email.fr",
            first_name="inactive", last_name="inactive",
            customer=self.customer)
        self.inactive.is_active = False
        self.inactive.save()

    def test_login_su(self):
        self._test_login("root")

    def test_login_nobody(self):
        response = self._test_login("nobody")
        self.assertDictContainsSubset({
            'first_name': u"firstname",
            'last_name': u"lastname",
        }, response.data["user"])

    def test_badlogin(self):
        response = self._test_login("root", password="pouet", shouldpass=False)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictContainsSubset(
            {
                'isLogged': False,
                'active': False
            },
            response.data)

    def test_inactive(self):
        response = self._test_login("inactive", shouldpass=False)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictContainsSubset(
            {
                'isLogged': False,
                'active': False
            },
            response.data)

    def test_logout(self):
        self._test_login("nobody", first_name='', last_name='')
        logout_r = self.client.get(reverse('api-logout'))
        self.assertEqual(logout_r.status_code, status.HTTP_200_OK)


class BasicTicketTestCase(EmptyCacheAPITestCase, BasicTestCase):
    def setUp(self):
        super(BasicTicketTestCase, self).setUp()
        State(label="new", index=1).save()
        State(label="closed", index=2).save()
        Priority(label="normal", index=1).save()
        Priority(label="high", index=2).save()

        self.customer = Customer(name="root")
        self.customer.save()
        self.su = User.objects.create_superuser(
            username="root", password="root", email="root@email.fr",
            first_name="root", last_name="root",
            customer=self.customer)

    def test_permissions(self):
        for view in ("api-ticket-state-list", "api-ticket-priority-list",
                     "api-ticket-list"):
            response = self.client.get(reverse(view))
            self.assertEqual(response.status_code,
                             status.HTTP_403_FORBIDDEN)

    def test_priority_list(self):
        self._test_login("root")
        url = reverse("api-ticket-priority-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Priority.objects.all().count())

    def test_state_list(self):
        self._test_login("root")
        url = reverse("api-ticket-state-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), State.objects.all().count())

    def test_ticket_list_basic(self):
        self._test_login("root")
        url = reverse("api-ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Limit 50 but we don't have 50 ticket in our test data.
        self.assertEqual(
            response.data["count"],
            Ticket.objects.foruser(self.su).count(), response.data)
