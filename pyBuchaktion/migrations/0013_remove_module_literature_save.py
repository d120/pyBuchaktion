# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-05 21:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyBuchaktion', '0012_auto_20170605_2329'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='literature_save',
        ),
    ]
