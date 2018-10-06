# Generated by Django 2.1.1 on 2018-09-29 12:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0002_auto_20180928_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='birthday',
            field=models.DateField(default=django.utils.timezone.now, help_text='Required. Format: YYYY-MM-DD'),
        ),
    ]