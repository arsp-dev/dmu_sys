# Generated by Django 3.0.3 on 2023-10-16 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whonet', '0010_arspqualifyr'),
    ]

    operations = [
        migrations.AddField(
            model_name='finalantidisk',
            name='cza_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantidisk',
            name='czt_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantidisk',
            name='fdc_nd',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantidisk',
            name='imr_nd10',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantidisk',
            name='mev_nd20',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantidisk',
            name='plz_nd',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantietest',
            name='cza_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantietest',
            name='czt_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantietest',
            name='fdc_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantietest',
            name='imr_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantietest',
            name='mev_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantietest',
            name='plz_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantimic',
            name='cza_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantimic',
            name='czt_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantimic',
            name='fdc_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantimic',
            name='imr_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantimic',
            name='mev_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='finalantimic',
            name='plz_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidisk',
            name='cza_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidisk',
            name='czt_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidisk',
            name='fdc_nd',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidisk',
            name='imr_nd10',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidisk',
            name='mev_nd20',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidisk',
            name='plz_nd',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidiskris',
            name='cza_nd30_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidiskris',
            name='czt_nd30_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidiskris',
            name='fdc_nd_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidiskris',
            name='imr_nd10_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidiskris',
            name='mev_nd20_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantidiskris',
            name='plz_nd_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimic',
            name='cza_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimic',
            name='czt_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimic',
            name='fdc_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimic',
            name='imr_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimic',
            name='mev_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimic',
            name='plz_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimicris',
            name='cza_nm_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimicris',
            name='czt_nm_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimicris',
            name='fdc_nm_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimicris',
            name='imr_nm_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimicris',
            name='mev_nm_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='referredantimicris',
            name='plz_nm_ris',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
