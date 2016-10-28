# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-21 07:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('event', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_type', models.CharField(choices=[('DEFAULT', ''), ('NEWUSER', 'user registered on woozup'), ('NEWPARTICIPANT', 'user joins an event'), ('NEWEVENT', 'user created an event'), ('NEWFRIEND', 'user connected with another user')], default='DEFAULT', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='\nautofield, not modifiable')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='\nautofield, not modifiable')),
                ('refering_event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='event.Event')),
                ('refering_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Records as user+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
