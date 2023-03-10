# Generated by Django 4.1.5 on 2023-01-17 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PN", "Pending"), ("PD", "Paid")], max_length=2
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("PN", "Payment"), ("FN", "Fine")], max_length=2
                    ),
                ),
            ],
        ),
    ]
