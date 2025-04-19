from django.db import migrations

def create_topics_and_update_references(apps, schema_editor):
    Topic = apps.get_model('search_app', 'Topic')
    QuizQuestion = apps.get_model('search_app', 'QuizQuestion')
    QuizAttempt = apps.get_model('quiz', 'QuizAttempt')
    
    # Get all unique topics from QuizQuestion and QuizAttempt
    quiz_topics = set(QuizQuestion.objects.values_list('topic', flat=True).distinct())
    attempt_topics = set(QuizAttempt.objects.values_list('topic', flat=True).distinct())
    all_topics = quiz_topics.union(attempt_topics)
    
    # Create Topic objects
    topic_mapping = {}
    for topic_name in all_topics:
        if topic_name:  # Skip empty topics
            topic_obj = Topic.objects.create(name=topic_name, content='')
            topic_mapping[topic_name] = topic_obj
    
    # Update QuizQuestion references
    for question in QuizQuestion.objects.all():
        if question.topic in topic_mapping:
            question.topic = topic_mapping[question.topic]
            question.save()
    
    # Update QuizAttempt references
    for attempt in QuizAttempt.objects.all():
        if attempt.topic in topic_mapping:
            attempt.topic = topic_mapping[attempt.topic]
            attempt.save()

def reverse_migration(apps, schema_editor):
    Topic = apps.get_model('search_app', 'Topic')
    Topic.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('search_app', '0001_initial'),
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_topics_and_update_references, reverse_migration),
    ] 