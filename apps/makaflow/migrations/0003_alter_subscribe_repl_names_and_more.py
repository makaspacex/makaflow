# Generated by Django 4.2.10 on 2024-02-29 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('makaflow', '0002_remove_subscribe_sub_groups_delete_subgroup_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='repl_names',
            field=models.CharField(blank=True, max_length=256, verbose_name='名称替换'),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='server_mirr',
            field=models.CharField(blank=True, max_length=256, verbose_name='镜像地址替换'),
        ),
    ]
