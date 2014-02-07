import re
from django.db import models
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, UserManager)
from django.core import validators
from django.utils import timezone
from customer.models import Customer


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'), max_length=128, unique=True,
        help_text=_('Required. 128 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'),
                                      _('Enter a valid username.'),
                                      'invalid')
        ])
    email = models.EmailField(_('email address'), max_length=256, blank=True,
                              db_index=True)
    first_name = models.CharField(_('first name'), max_length=256, blank=True)
    last_name = models.CharField(_('last name'), max_length=256, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    customer = models.ForeignKey(
        Customer,
        help_text=_("Which customer this user belongs to"),
        db_index=True)
    security_level = models.IntegerField(_("Security level"), default=0)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'customer']

    class Meta:
        verbose_name = _("User")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_visible_customers(self):
        return self.customer.get_descendants(include_self=True)


class AccessLog(models.Model):
    """Generic access log"""
    class Meta:
        ordering = ["-date", ]

    ACCESSLOG_CHOICES = (
        ('AUTH_OK', _("Authentification successfull")),
        ('AUTH_BAD', _("Authentification failed")),
    )
    user = models.ForeignKey(
        User, db_index=True, blank=True, null=True,
        related_name="login_accesslog")
    username = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    message = models.CharField(max_length=32, choices=ACCESSLOG_CHOICES)
    ip = models.GenericIPAddressField(unpack_ipv4=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.user and not self.username:
            self.username = self.user.username
        return super(AccessLog, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s (%s): %s" % (self.user.username, self.ip, self.message)

    def __repr__(self):
        return "<AccessLog: %s: %s>" % (self.user.username, self.message)
