# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0001_initial'),
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='receiver',
            field=models.ForeignKey(related_name='link_as_receiver', to='userprofile.UserProfile'),
        ),
        migrations.AddField(
            model_name='link',
            name='sender',
            field=models.ForeignKey(related_name='link_as_sender', to='userprofile.UserProfile'),
        ),
        migrations.AddField(
            model_name='invite',
            name='sender',
            field=models.ForeignKey(to='userprofile.UserProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='link',
            unique_together=set([('sender', 'receiver')]),
        ),
        migrations.AlterUniqueTogether(
            name='invite',
            unique_together=set([('sender', 'number')]),
        ),
    ]
