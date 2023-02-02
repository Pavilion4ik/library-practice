from django.core.validators import MinValueValidator
from django.db import models


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book_id = models.IntegerField(validators=[MinValueValidator(1)])
    user_id = models.IntegerField(validators=[MinValueValidator(1)])
