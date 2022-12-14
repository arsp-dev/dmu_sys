# Generated by Django 3.0.3 on 2021-11-03 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whonet', '0003_ghruqualifyr'),
    ]

    operations = [
        migrations.AddField(
            model_name='ghruqualifyr',
            name='address_latitude_outpatients_only',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='address_longitude_outpatients_only',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='address_outpatients_only',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='clinical_diagnosis',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='clinical_significance',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='collected_by',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='collection_contact',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='collection_date',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='country',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='country_alpha_2_code',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='day',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='ghru_uuid',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='hai_type',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='host',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='invasive',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='iso_3166_2_subdivision_code',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='latitude',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='location',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='longitude',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='month',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='origin',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='outbreak_isolate',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='patient_age',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='patient_date_of_birth',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='patient_gender',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='patient_type',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='region_province_department',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='room_inpatients_only',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='sentinel_site_code',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='specimen_type',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='ward_inpatients_only',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='wgs_id',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='wgs_qc',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='ghruqualifyr',
            name='year',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
