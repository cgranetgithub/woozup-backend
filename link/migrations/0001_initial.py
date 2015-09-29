# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import service.utils


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'name to be displayed in the app', max_length=255, blank=True)),
                ('numbers', models.CharField(help_text='phone numbers list', max_length=255, blank=True)),
                ('emails', models.CharField(help_text='email addresses list', max_length=255, blank=True)),
                ('photo', models.CharField(help_text=b'local path in the device to a picture', max_length=255, blank=True)),
                ('avatar', models.ImageField(help_text=b'not used for now', null=True, upload_to=service.utils.image_path, blank=True)),
                ('status', models.CharField(default=b'NEW', max_length=3, choices=[(b'NEW', b'new'), (b'PEN', b'pending'), (b'ACC', b'accepted'), (b'IGN', b'ignored'), (b'CLO', b'closed')])),
                ('sent_at', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now_add=True)),
                ('updated_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now=True)),
                ('sender', models.ForeignKey(to='userprofile.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender_status', models.CharField(default=b'NEW', max_length=3, choices=[(b'NEW', b'new'), (b'PEN', b'pending'), (b'ACC', b'accepted'), (b'REJ', b'rejected'), (b'IGN', b'ignored'), (b'BLO', b'blocked')])),
                ('receiver_status', models.CharField(default=b'NEW', max_length=3, choices=[(b'NEW', b'new'), (b'PEN', b'pending'), (b'ACC', b'accepted'), (b'REJ', b'rejected'), (b'IGN', b'ignored'), (b'BLO', b'blocked')])),
                ('sent_at', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now_add=True)),
                ('updated_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now=True)),
                ('receiver', models.ForeignKey(related_name='link_as_receiver', to='userprofile.UserProfile')),
                ('sender', models.ForeignKey(related_name='link_as_sender', to='userprofile.UserProfile')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='link',
            unique_together=set([('sender', 'receiver')]),
        ),
        migrations.AlterUniqueTogether(
            name='invite',
            unique_together=set([('sender', 'numbers'), ('sender', 'emails')]),
        ),
    ]
