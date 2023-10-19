# Generated by Django 3.0.3 on 2023-10-19 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whonet', '0013_auto_20231017_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='finalantidisk',
            name='amx_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantietest',
            name='amx_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantimic',
            name='amx_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantidisk',
            name='amx_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantietest',
            name='amx_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantimic',
            name='amx_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidisk',
            name='amx_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidiskris',
            name='amx_nd30_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimic',
            name='amx_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimicris',
            name='amx_nm_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
