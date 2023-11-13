# Generated by Django 4.2.3 on 2023-11-08 23:17

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
                ('khaleesiVersion', models.IntegerField(default=0)),
                ('khaleesiId', models.TextField(editable=False, unique=True)),
                ('khaleesiCreated', models.DateTimeField(auto_now_add=True)),
                ('khaleesiCreatedById', models.TextField()),
                ('khaleesiCreatedByType', models.TextField()),
                ('khaleesiModified', models.DateTimeField(auto_now=True)),
                ('khaleesiModifiedById', models.TextField()),
                ('khaleesiModifiedByType', models.TextField()),
                ('site', models.TextField(default='UNKNOWN')),
                ('app', models.TextField(default='UNKNOWN')),
                ('action', models.TextField(default='UNKNOWN')),
                ('actionTimelimit', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('actionBatchSize', models.IntegerField(default=1000)),
                ('cleanupIs', models.BooleanField(default=False)),
                ('cleanupSince', models.DateTimeField(default=datetime.datetime.now)),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField()),
                ('cronExpression', models.TextField()),
            ],
            options={
                'ordering': ['pk'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JobExecution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jobId', models.TextField()),
                ('status', models.TextField(default='UNKNOWN')),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('statusDetails', models.TextField()),
                ('itemsProcessed', models.IntegerField(default=0)),
                ('totalItems', models.IntegerField(default=0)),
                ('khaleesiVersion', models.IntegerField(default=0)),
                ('khaleesiId', models.TextField(editable=False, unique=True)),
                ('site', models.TextField(default='UNKNOWN')),
                ('app', models.TextField(default='UNKNOWN')),
                ('action', models.TextField(default='UNKNOWN')),
                ('actionTimelimit', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('actionBatchSize', models.IntegerField(default=1000)),
                ('cleanupIs', models.BooleanField(default=False)),
                ('cleanupSince', models.DateTimeField(default=datetime.datetime.now)),
                ('start', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['pk'],
                'abstract': False,
            },
        ),
    ]
