# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import service.utils


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, blank=True)),
                ('comment', models.CharField(max_length=255, blank=True)),
                ('special', models.BooleanField(default=False)),
                ('public', models.BooleanField(default=False)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(null=True, blank=True)),
                ('closed', models.BooleanField(default=False, help_text='if closed no more participants accepted')),
                ('p_limit', models.IntegerField(help_text='maximum number of participants', null=True, blank=True)),
                ('position', django.contrib.gis.db.models.fields.GeometryField(help_text='Type: Geometry, Entry format: GeoJson \n(example: "{ \'type\':\'Point\', \'coordinates\':[125.6, 10.1] }")<br>', srid=4326, null=True, blank=True)),
                ('image', models.ImageField(null=True, upload_to=service.utils.image_path, blank=True)),
                ('created_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now_add=True)),
                ('updated_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('short_name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=255)),
                ('order', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('image', models.ImageField(upload_to=b'glyph')),
                ('created_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now_add=True)),
                ('updated_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('short_name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=255)),
                ('order', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('image', models.ImageField(null=True, upload_to=b'glyph', blank=True)),
                ('created_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now_add=True)),
                ('updated_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now=True)),
                ('category', models.ManyToManyField(to='event.EventCategory')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(to='event.EventType'),
        ),
    ]