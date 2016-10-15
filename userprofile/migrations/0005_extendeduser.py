# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-14 12:19
from __future__ import unicode_literals

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('userprofile', '0004_auto_20161010_1334'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
