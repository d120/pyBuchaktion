# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-05 21:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyBuchaktion', '0009_auto_20170601_1559'),
    ]

    operations = [
        migrations.CreateModel(
            name='Literature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(choices=[('TC', 'TUCaN Export'), ('SF', 'Module Staff'), ('SD', 'Student')], default='TC', max_length=2, verbose_name='source')),
            ],
            options={
                'verbose_name': 'literature',
            },
        ),
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title'], 'verbose_name': 'book', 'verbose_name_plural': 'books'},
        ),
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ['module_id'], 'verbose_name': 'module', 'verbose_name_plural': 'modules'},
        ),
        migrations.RenameField(
            model_name='module',
            old_name='literature',
            new_name='literature_save',
        ),
        migrations.AddField(
            model_name='literature',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='literature_info', to='pyBuchaktion.Book'),
        ),
        migrations.AddField(
            model_name='literature',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='literature_info', to='pyBuchaktion.Module'),
        ),
    ]