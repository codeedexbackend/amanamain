# Generated by Django 5.0.1 on 2024-02-15 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='measurements',
        ),
    ]