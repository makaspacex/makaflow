# Generated by Django 5.0.1 on 2024-01-12 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('status', models.IntegerField(choices=[(-1, '已删除'), (0, '禁用'), (1, '正常')], default=1, verbose_name='状态')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='名称')),
                ('rule', models.CharField(max_length=256, verbose_name='正则表达式')),
            ],
            options={
                'verbose_name': '规则',
                'verbose_name_plural': '规则管理',
            },
        ),
        migrations.CreateModel(
            name='SystemConfig',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('status', models.IntegerField(choices=[(-1, '已删除'), (0, '禁用'), (1, '正常')], default=1, verbose_name='状态')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='名称')),
                ('rule', models.CharField(max_length=256, verbose_name='正则表达式')),
            ],
            options={
                'verbose_name': '规则',
                'verbose_name_plural': '规则管理',
            },
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('status', models.IntegerField(choices=[(-1, '已删除'), (0, '禁用'), (1, '正常')], default=1, verbose_name='状态')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=256, null=True, verbose_name='名称')),
                ('sub_enable', models.BooleanField(default=True, verbose_name='可订阅')),
                ('prefix', models.CharField(blank=True, max_length=256, null=True, verbose_name='前缀')),
                ('use_proxy', models.BooleanField(default=True, verbose_name='通过代理')),
                ('sub_url', models.CharField(max_length=256, verbose_name='订阅地址')),
                ('repl_names', models.JSONField(blank=True, null=True, verbose_name='名称替换')),
                ('content', models.TextField(blank=True, null=True, verbose_name='订阅内容')),
                ('server_mirr', models.JSONField(blank=True, null=True, verbose_name='镜像地址替换')),
                ('node_excludes', models.ManyToManyField(blank=True, null=True, to='makaflow.rule', verbose_name='排除规则')),
            ],
            options={
                'verbose_name': '订阅',
                'verbose_name_plural': '订阅管理',
            },
        ),
    ]
