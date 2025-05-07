from django.core.management.base import BaseCommand
from quiz.models import QuizAttempt

class Command(BaseCommand):
    help = 'Backfill the score field for all existing QuizAttempts based on their QuestionAttempts.'

    def handle(self, *args, **options):
        updated = 0
        for attempt in QuizAttempt.objects.all():
            total_score = sum(q.score for q in attempt.question_attempts.all())
            if attempt.score != total_score:
                attempt.score = total_score
                attempt.save(update_fields=["score"])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Backfilled scores for {updated} QuizAttempt(s).'))
