# Generated by Django 4.1.3 on 2023-01-16 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_profile_profile_alter_event_gallery_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pronouns',
            field=models.CharField(choices=[('he', 'He/Him/His'), ('she', 'She/Her/Hers'), ('they', 'They/Them/Theirs')], default='she', max_length=32),
        ),
    ]
