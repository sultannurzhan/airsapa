# Generated by Django 4.2.16 on 2024-11-18 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_userprofile_alter_historicaldata_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='email',
        ),
    ]