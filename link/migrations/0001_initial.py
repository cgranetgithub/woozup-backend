# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import service.utils


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(help_text='phone number', max_length=50)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('name', models.CharField(help_text=b'name to be displayed in the app', max_length=255, blank=True)),
                ('photo', models.CharField(help_text=b'local path in the device to a picture', max_length=255, blank=True)),
                ('avatar', models.ImageField(help_text=b'not used for now', null=True, upload_to=service.utils.image_path, blank=True)),
                ('status', models.CharField(default=b'NEW', max_length=3, choices=[(b'NEW', b'new'), (b'PEN', b'pending'), (b'ACC', b'accepted'), (b'IGN', b'ignored'), (b'CLO', b'closed')])),
                ('sent_at', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now_add=True)),
                ('updated_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now=True)),
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
            ],
        ),
    ]
