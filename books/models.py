from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HR", _("Hard")
        SOFT = "ST", _("Soft")

    title = models.CharField(max_length=255, null=False, blank=False)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=2, choices=Cover.choices)
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(max_digits=4, decimal_places=2)
