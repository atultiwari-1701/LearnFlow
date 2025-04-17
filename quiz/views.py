import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import QuizAttempt, QuestionAttempt
from search_app.models import QuizQuestion

# Create your views here.
def save_quiz_attempt(request):
    # Check if request method is POST
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

    try:
        data = json.loads(request.body)
        
        # Create the quiz attempt
        quiz_attempt = QuizAttempt.objects.create(
            user_id=data['user_id'],
            total_time_taken=data['total_time_taken'],
            score=data['score'],
            correct_attempts=data['correct_attempts'],
            incorrect_attempts=data['incorrect_attempts'],
            partial_attempts=data['partial_attempts'],
            unattempted=data['unattempted']
        )
        
        # Create question attempts
        for question_data in data['question_attempts']:
            try:
                question = QuizQuestion.objects.get(id=question_data['question_id'])
                QuestionAttempt.objects.create(
                    quiz_attempt=quiz_attempt,
                    question=question,
                    time_taken=question_data['time_taken'],
                    attempted_options=question_data['attempted_options']
                )
            except QuizQuestion.DoesNotExist:
                # Skip if question doesn't exist
                continue
        
        # Keep only the latest 5 attempts for this user
        # First get all attempts ordered by creation date
        all_attempts = QuizAttempt.objects.filter(
            user_id=data['user_id']
        ).order_by('-created_at')
        
        # If there are more than 5 attempts, delete the older ones
        if all_attempts.count() > 5:
            # Get IDs of attempts to keep (latest 5)
            keep_ids = list(all_attempts.values_list('id', flat=True)[:5])
            # Delete all attempts except the ones to keep
            QuizAttempt.objects.filter(
                user_id=data['user_id']
            ).exclude(id__in=keep_ids).delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Quiz attempt saved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)