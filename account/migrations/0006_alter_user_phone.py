# Generated by Django 4.2.5 on 2024-08-09 04:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0005_alter_user_is_deleted"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(
                db_index=True,
                unique=True,
                validators=[django.core.validators.RegexValidator(regex="^09\\d{9}$")],
            ),
        ),
    ]