# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventtype',
            name='image',
        ),
        migrations.AddField(
            model_name='eventtype',
            name='background',
            field=models.ImageField(null=True, upload_to=b'type_bg', blank=True),
        ),
        migrations.AddField(
            model_name='eventtype',
            name='icon',
            field=models.ImageField(null=True, upload_to=b'type_icon', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(null=True, upload_to=b'event_image', blank=True),
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='image',
            field=models.ImageField(upload_to=b'category_image'),
        ),
    ]
