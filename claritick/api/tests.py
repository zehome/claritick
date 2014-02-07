# -*- coding: utf-8 -*-

import datetime
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from claritick.models import User
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
