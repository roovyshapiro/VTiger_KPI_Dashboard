# Generated by Django 3.0.7 on 2021-03-03 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdtime', models.DateTimeField(null=True)),
                ('modifiedtime', models.DateTimeField(null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('assigned_user_id', models.CharField(max_length=50)),
                ('created_user_id', models.CharField(max_length=50)),
                ('modified_by', models.CharField(max_length=50)),
                ('assigned_username', models.CharField(max_length=50)),
                ('modified_username', models.CharField(default='', max_length=75)),
                ('product_id', models.CharField(max_length=50)),
                ('url_id', models.CharField(default='', max_length=50)),
                ('image_id', models.CharField(max_length=50)),
                ('image_url_id', models.CharField(max_length=50)),
                ('width', models.IntegerField()),
                ('length', models.IntegerField()),
                ('height', models.IntegerField()),
                ('weight', models.IntegerField()),
                ('description', models.TextField()),
                ('packing_list', models.TextField()),
                ('number', models.CharField(max_length=10)),
                ('category', models.CharField(max_length=25)),
                ('name', models.CharField(max_length=50)),
                ('stock', models.CharField(max_length=50)),
                ('price', models.FloatField()),
                ('status', models.CharField(max_length=50)),
            ],
        ),
    ]
