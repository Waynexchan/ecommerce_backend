# Generated by Django 5.0.6 on 2024-06-05 22:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_alter_tax_options_alter_cart_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartorder',
            old_name='town',
            new_name='city',
        ),
    ]
