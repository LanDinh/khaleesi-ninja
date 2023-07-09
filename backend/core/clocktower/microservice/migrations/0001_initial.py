# Generated by Django 4.0.5 on 2023-07-09 21:54

import abc
import datetime
from django.db import migrations, models
import typing


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actionTimelimit', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('actionBatchSize', models.IntegerField(default=1000)),
                ('cleanupIs', models.BooleanField(default=False)),
                ('cleanupDelay', models.DurationField(default=datetime.timedelta(0))),
                ('khaleesiVersion', models.IntegerField(default=0)),
                ('khaleesiId', models.TextField(editable=False, unique=True)),
                ('khaleesiCreated', models.DateTimeField(auto_now_add=True)),
                ('khaleesiCreatedById', models.TextField()),
                ('khaleesiCreatedByType', models.TextField()),
                ('khaleesiModified', models.DateTimeField(auto_now=True)),
                ('khaleesiModifiedById', models.TextField()),
                ('khaleesiModifiedByType', models.TextField()),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('cronExpression', models.TextField()),
                ('action', models.TextField(default='UNKNOWN')),
            ],
            options={
                'ordering': ['pk'],
                'abstract': False,
            },
        ),
    ]
