# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-02 02:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='directoryentry',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]
