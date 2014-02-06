from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Customer(MPTTModel):
    class Meta:
        verbose_name = _("Customer")
        ordering = ['name', ]

    class MPTTMeta:
        order_insertion_by = ['name']

    name = models.CharField(_("Name"), max_length=64)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
