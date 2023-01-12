# Generated by Django 4.0.5 on 2023-01-12 16:57

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BackgateRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_caller_backgate_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_gate', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_method', models.TextField(default='UNKNOWN')),
                ('meta_caller_pod_id', models.TextField(default='UNKNOWN')),
                ('meta_user_id', models.TextField(default='UNKNOWN')),
                ('meta_user_type', models.IntegerField(default=0)),
                ('meta_reported_timestamp', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('meta_logged_timestamp', models.DateTimeField(auto_now_add=True)),
                ('meta_logging_errors', models.TextField(blank=True)),
                ('meta_response_status', models.TextField(default='IN_PROGRESS')),
                ('meta_response_reported_timestamp', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('meta_response_logged_timestamp', models.DateTimeField(auto_now=True)),
                ('meta_response_logging_errors', models.TextField(blank=True)),
                ('type', models.TextField(default='UNKNOWN')),
                ('language', models.TextField(default='UNKNOWN')),
                ('device_id', models.TextField(default='UNKNOWN')),
                ('language_header', models.TextField(default='UNKNOWN')),
                ('ip', models.TextField(default='UNKNOWN')),
                ('useragent', models.TextField(default='UNKNOWN')),
                ('geolocation', models.TextField(default='UNKNOWN')),
                ('browser', models.TextField(default='UNKNOWN')),
                ('rendering_agent', models.TextField(default='UNKNOWN')),
                ('os', models.TextField(default='UNKNOWN')),
                ('device_type', models.TextField(default='UNKNOWN')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_caller_backgate_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_gate', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_method', models.TextField(default='UNKNOWN')),
                ('meta_caller_pod_id', models.TextField(default='UNKNOWN')),
                ('meta_user_id', models.TextField(default='UNKNOWN')),
                ('meta_user_type', models.IntegerField(default=0)),
                ('meta_reported_timestamp', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('meta_logged_timestamp', models.DateTimeField(auto_now_add=True)),
                ('meta_logging_errors', models.TextField(blank=True)),
                ('error_id', models.TextField(default='UNKNOWN')),
                ('status', models.TextField(default='UNKNOWN')),
                ('loglevel', models.TextField(default='FATAL')),
                ('gate', models.TextField(default='UNKNOWN')),
                ('service', models.TextField(default='UNKNOWN')),
                ('public_key', models.TextField(default='UNKNOWN')),
                ('public_details', models.TextField(default='')),
                ('private_message', models.TextField(default='')),
                ('private_details', models.TextField(default='')),
                ('stacktrace', models.TextField(default='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_caller_backgate_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_gate', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_method', models.TextField(default='UNKNOWN')),
                ('meta_caller_pod_id', models.TextField(default='UNKNOWN')),
                ('meta_user_id', models.TextField(default='UNKNOWN')),
                ('meta_user_type', models.IntegerField(default=0)),
                ('meta_reported_timestamp', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('meta_logged_timestamp', models.DateTimeField(auto_now_add=True)),
                ('meta_logging_errors', models.TextField(blank=True)),
                ('event_id', models.TextField(default='UNKNOWN')),
                ('target_type', models.TextField(default='UNKNOWN')),
                ('target_id', models.TextField(default='UNKNOWN')),
                ('target_owner_id', models.TextField(default='UNKNOWN')),
                ('target_owner_type', models.TextField(default='UNKNOWN')),
                ('action_crud_type', models.TextField(default='UNKNOWN_ACTION')),
                ('action_custom_type', models.TextField(default='UNKNOWN')),
                ('action_result', models.TextField(default='UNKNOWN_RESULT')),
                ('action_details', models.TextField(default='UNKNOWN')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_caller_backgate_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_gate', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_method', models.TextField(default='UNKNOWN')),
                ('meta_caller_pod_id', models.TextField(default='UNKNOWN')),
                ('meta_user_id', models.TextField(default='UNKNOWN')),
                ('meta_user_type', models.IntegerField(default=0)),
                ('meta_reported_timestamp', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('meta_logged_timestamp', models.DateTimeField(auto_now_add=True)),
                ('meta_logging_errors', models.TextField(blank=True)),
                ('query_id', models.TextField(default='UNKNOWN')),
                ('raw', models.TextField(default='UNKNOWN')),
                ('normalized', models.TextField(default='UNKNOWN')),
                ('tables', models.TextField(default='UNKNOWN')),
                ('columns', models.TextField(default='UNKNOWN')),
                ('reported_start', models.DateTimeField()),
                ('reported_end', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_caller_backgate_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_request_id', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_gate', models.TextField(default='UNKNOWN')),
                ('meta_caller_khaleesi_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_service', models.TextField(default='UNKNOWN')),
                ('meta_caller_grpc_method', models.TextField(default='UNKNOWN')),
                ('meta_caller_pod_id', models.TextField(default='UNKNOWN')),
                ('meta_user_id', models.TextField(default='UNKNOWN')),
                ('meta_user_type', models.IntegerField(default=0)),
                ('meta_reported_timestamp', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('meta_logged_timestamp', models.DateTimeField(auto_now_add=True)),
                ('meta_logging_errors', models.TextField(blank=True)),
                ('meta_response_status', models.TextField(default='IN_PROGRESS')),
                ('meta_response_reported_timestamp', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('meta_response_logged_timestamp', models.DateTimeField(auto_now=True)),
                ('meta_response_logging_errors', models.TextField(blank=True)),
                ('upstream_request_request_id', models.TextField(default='UNKNOWN')),
                ('upstream_request_khaleesi_gate', models.TextField(default='UNKNOWN')),
                ('upstream_request_khaleesi_service', models.TextField(default='UNKNOWN')),
                ('upstream_request_grpc_service', models.TextField(default='UNKNOWN')),
                ('upstream_request_grpc_method', models.TextField(default='UNKNOWN')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceRegistryKhaleesiGate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRegistryKhaleesiService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('khaleesi_gate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='khaleesi_services', to='microservice.serviceregistrykhaleesigate')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRegistryGrpcService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('khaleesi_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grpc_services', to='microservice.serviceregistrykhaleesiservice')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRegistryGrpcMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('grpc_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grpc_methods', to='microservice.serviceregistrygrpcservice')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRegistryGrpcCall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('called', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calls', to='microservice.serviceregistrygrpcmethod')),
                ('caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='called_by', to='microservice.serviceregistrygrpcmethod')),
            ],
        ),
    ]
