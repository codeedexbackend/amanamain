# Generated by Django 3.2.10 on 2024-03-04 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0020_reception_login'),
    ]

    operations = [
        migrations.CreateModel(
            name='admin_login',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=20, null=True)),
                ('password', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]