# Generated by Django 3.2 on 2021-05-07 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_address_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='address',
            name='longitude',
            field=models.FloatField(),
        ),
    ]
