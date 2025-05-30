# Generated by Django 5.1.6 on 2025-04-19 20:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('quiz', '0004_alter_quizattempt_subtopic_alter_quizattempt_topic'),
        ('search_app', '0008_rename_search_app__topic_e39d4c_idx_search_app__topic_i_4051e9_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizattempt',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_attempts', to='search_app.topic'),
        ),
        migrations.AddIndex(
            model_name='quizattempt',
            index=models.Index(fields=['topic'], name='quiz_quizat_topic_i_06f972_idx'),
        ),
    ]
