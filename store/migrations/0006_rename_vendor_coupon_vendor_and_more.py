# Generated by Django 5.0.6 on 2024-06-02 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_product_options_coupon_notification_productfaq_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coupon',
            old_name='Vendor',
            new_name='vendor',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='Vendor',
            new_name='vendor',
        ),
    ]