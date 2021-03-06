# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-25 10:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host_monitor', '0014_auto_20180119_1830'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pod',
            old_name='hostport',
            new_name='host_port',
        ),
        migrations.AddField(
            model_name='pod',
            name='host_ip',
            field=models.GenericIPAddressField(blank=True, null=True, unique=True, verbose_name='对外IP'),
        ),
    ]
