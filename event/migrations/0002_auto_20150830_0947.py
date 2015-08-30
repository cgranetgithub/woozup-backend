# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(related_name='events_as_owner', to='userprofile.UserProfile'),
        ),
        migrations.AddField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(related_name='events_as_participant', to='userprofile.UserProfile', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('start', 'event_type', 'owner')]),
        ),
    ]
