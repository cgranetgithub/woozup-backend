# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-30 19:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_auto_20161129_1048'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-updated_at']},
        ),
    ]
