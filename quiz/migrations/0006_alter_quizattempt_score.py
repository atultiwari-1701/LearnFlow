# Generated by Django 5.1.6 on 2025-05-07 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_alter_quizattempt_topic_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizattempt',
            name='score',
            field=models.IntegerField(default=0, help_text='Total score for this quiz attempt'),
        ),
    ]
