# Generated by Django 4.2.20 on 2025-04-22 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0007_alter_advert_views'),
        ('authentication', '0003_alter_onetimepassword_options_alter_profile_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='liked_adverts',
            field=models.ManyToManyField(
                blank=True, related_name='users_likes', to='booking.advert', verbose_name='Понравившиеся объявления'
            ),
        ),
    ]
