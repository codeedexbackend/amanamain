# Generated by Django 5.0.1 on 2024-02-19 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0028_addcustomer_cuftype_alter_addcustomer_cuf'),
    ]

    operations = [
        migrations.RenameField(
            model_name='addtailor',
            old_name='tailor_name',
            new_name='tailorname',
        ),
        migrations.AlterField(
            model_name='addcustomer',
            name='cuf',
            field=models.CharField(default='1', max_length=15),
        ),
        migrations.AlterField(
            model_name='addcustomer',
            name='length',
            field=models.CharField(default='1', max_length=15),
        ),
        migrations.AlterField(
            model_name='addcustomer',
            name='loose',
            field=models.CharField(default='1', max_length=15),
        ),
        migrations.AlterField(
            model_name='addcustomer',
            name='neck',
            field=models.CharField(default='1', max_length=15),
        ),
        migrations.AlterField(
            model_name='addcustomer',
            name='regal',
            field=models.CharField(default='1', max_length=15),
        ),
        migrations.AlterField(
            model_name='addcustomer',
            name='shoulder',
            field=models.CharField(default='1', max_length=15),
        ),
        migrations.AlterField(
            model_name='addcustomer',
            name='sleeve',
            field=models.CharField(default='1', max_length=15),
        ),
    ]
