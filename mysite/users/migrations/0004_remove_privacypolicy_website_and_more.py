# Generated by Django 5.0.7 on 2024-07-27 10:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_additional_email_user_contact_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='privacypolicy',
            name='website',
        ),
        migrations.RemoveField(
            model_name='privacypolicy',
            name='publish_date',
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='site_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='url',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='full_text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='summary_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.DeleteModel(
            name='UserHistory',
        ),
        migrations.DeleteModel(
            name='Website',
        ),
    ]
