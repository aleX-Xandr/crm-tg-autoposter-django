# Generated by Django 4.2.5 on 2024-03-20 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mymodel',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
