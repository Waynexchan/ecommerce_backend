# Generated by Django 5.0.6 on 2024-06-16 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_remove_color_date_alter_color_color_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
