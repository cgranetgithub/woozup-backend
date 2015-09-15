# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
from django.conf import settings
import phonenumber_field.modelfields
import service.utils


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPosition',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('last', django.contrib.gis.db.models.fields.GeometryField(help_text='\nType: Geometry, Entry format: GeoJson (example: "{ \'type\' : \'Point\',\n\'coordinates\' : [125.6, 10.1] }")<br>', srid=4326, null=True, blank=True)),
                ('home', django.contrib.gis.db.models.fields.GeometryField(help_text='\nType: Geometry, Entry format: GeoJson (example: "{ \'type\' : \'Point\',\n\'coordinates\' : [125.6, 10.1] }")<br>', srid=4326, null=True, blank=True)),
                ('office', django.contrib.gis.db.models.fields.GeometryField(help_text='\nType: Geometry, Entry format: GeoJson (example: "{ \'type\' : \'Point\',\n\'coordinates\' : [125.6, 10.1] }")<br>', srid=4326, null=True, blank=True)),
                ('updated_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('gender', models.CharField(blank=True, max_length=2, choices=[(b'MA', b'male'), (b'FE', b'female')])),
                ('birth_date', models.DateField(null=True, blank=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, blank=True)),
                ('locale', models.CharField(max_length=3, blank=True)),
                ('image', models.ImageField(null=True, upload_to=service.utils.image_path, blank=True)),
                ('updated_at', models.DateTimeField(help_text='\nautofield, not modifiable', auto_now=True)),
            ],
        ),
    ]
