# Generated by Django 4.2.8 on 2024-12-06 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_remove_userprofile_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
