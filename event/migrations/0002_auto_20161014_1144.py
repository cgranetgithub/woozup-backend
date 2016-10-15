# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-14 11:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='invitees',
            field=models.ManyToManyField(blank=True, related_name='events_as_invitee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events_as_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='events_as_participant', to=settings.AUTH_USER_MODEL),
        ),
    ]
