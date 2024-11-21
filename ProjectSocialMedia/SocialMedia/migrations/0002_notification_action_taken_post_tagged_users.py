# Generated by Django 5.1.1 on 2024-11-19 12:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMedia', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='action_taken',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='tagged_users',
            field=models.ManyToManyField(blank=True, related_name='tagged_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
