# Generated by Django 4.2.5 on 2023-10-18 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdatabase',
            name='comment',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='admin',
            field=models.CharField(default='', max_length=255),
        ),
    ]
