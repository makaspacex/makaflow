# Generated by Django 4.2.10 on 2024-03-06 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('makaflow', '0004_repo_autoupdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='sub_url',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='订阅地址'),
        ),
    ]