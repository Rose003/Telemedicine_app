# Generated by Django 5.1.3 on 2024-11-22 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0002_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='admin',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='admin_profiles/'),
        ),
        migrations.AddField(
            model_name='admin',
            name='username',
            field=models.CharField(default='admin', max_length=45),
        ),
    ]