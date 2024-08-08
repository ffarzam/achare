# Generated by Django 4.2.5 on 2024-08-08 10:32

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0003_alter_user_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecycleUser",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("account.user",),
            managers=[
                ("deleted_object", django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="deleted_at",
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
    ]
