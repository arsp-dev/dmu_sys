# Generated by Django 3.0.3 on 2023-10-16 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whonet', '0011_auto_20231016_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawantidisk',
            name='cza_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantidisk',
            name='czt_nd30',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantidisk',
            name='fdc_nd',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantidisk',
            name='imr_nd10',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantidisk',
            name='mev_nd20',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantidisk',
            name='plz_nd',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantietest',
            name='cza_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantietest',
            name='czt_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantietest',
            name='fdc_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantietest',
            name='imr_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantietest',
            name='mev_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantietest',
            name='plz_ne',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantimic',
            name='cza_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantimic',
            name='czt_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantimic',
            name='fdc_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantimic',
            name='imr_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantimic',
            name='mev_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='rawantimic',
            name='plz_nm',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
