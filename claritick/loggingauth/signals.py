# -*- coding: utf-8 -*-

from django.dispatch import Signal

auth_username_failed = Signal(providing_args=["username"])
auth_password_failed = Signal(providing_args=["user"])
