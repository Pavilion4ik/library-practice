from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PN", _("Pending")
        PAID = "PD", _("Paid")

    class Type(models.TextChoices):
        PAYMENT = "PN", _("Payment")
        FINE = "FN", _("Fine")

    status = models.CharField(max_length=2, choices=Status.choices)
    type = models.CharField(max_length=2, choices=Type.choices)
