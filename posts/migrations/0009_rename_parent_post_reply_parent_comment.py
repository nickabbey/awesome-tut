# Generated by Django 4.2.11 on 2024-04-24 15:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_alter_comment_options_reply'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reply',
            old_name='parent_post',
            new_name='parent_comment',
        ),
    ]