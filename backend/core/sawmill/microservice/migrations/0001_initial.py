# Generated by Django 4.0 on 2022-01-12 20:55

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_caller_request_id', models.BigIntegerField(default=0)),
                ('meta_caller_khaleesi_gate', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_method', models.TextField(default='UNKNOWN')),
                ('meta_user_id', models.TextField(default='UNKNOWN')),
                ('meta_user_type', models.IntegerField(default=0)),
                ('meta_event_timestamp', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('meta_logged_timestamp', models.DateTimeField(auto_now_add=True)),
                ('meta_logging_errors', models.TextField(blank=True)),
                ('target_type', models.TextField(default='UNKNOWN')),
                ('target_id', models.BigIntegerField(default=0)),
                ('target_owner', models.UUIDField(blank=True, null=True)),
                ('action_crud_type', models.IntegerField(default=0)),
                ('action_custom_type', models.TextField(default='UNKNOWN')),
                ('action_result', models.IntegerField(default=0)),
                ('action_details', models.TextField(default='UNKNOWN')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
