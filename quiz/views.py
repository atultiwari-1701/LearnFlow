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
        
        # Validate required fields
        required_fields = ['user_id', 'total_time_taken', 'score', 'correct_attempts', 
                            'incorrect_attempts', 'partial_attempts', 'unattempted', 
                            'topic', 'subtopic', 'question_attempts']
        
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }, status=400)
        
        # Create the quiz attempt
        quiz_attempt = QuizAttempt.objects.create(
            user_id=data['user_id'],
            total_time_taken=data['total_time_taken'],
            score=data['score'],
            correct_attempts=data['correct_attempts'],
            incorrect_attempts=data['incorrect_attempts'],
            partial_attempts=data['partial_attempts'],
            unattempted=data['unattempted'],
            is_negative_marking=data.get('is_negative_marking', False),
            topic=data['topic'],
            subtopic=data['subtopic']
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
        
        return JsonResponse({
            'status': 'success',
            'message': 'Quiz attempt saved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)