# Generated by Django 4.2.5 on 2024-08-08 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_alter_user_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(default=False, verbose_name="active"),
        ),
    ]
