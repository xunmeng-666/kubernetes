# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-02 17:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('host_monitor', '0002_auto_20180102_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='namespaces',
            name='remark',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='master',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='host_monitor.Host', unique=True, verbose_name='主机'),
        ),
        migrations.AlterField(
            model_name='master',
            name='namespaces',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='host_monitor.NameSpaces', verbose_name='项目名称'),
        ),
    ]
