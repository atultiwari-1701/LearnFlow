import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import QuizAttempt, QuestionAttempt
from search_app.models import QuizQuestion, Topic
from django.core.serializers.json import DjangoJSONEncoder
from authentication.models import User

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
        
        # Get or create the Topic object
        topic_name = data['topic']
        try:
            topic = Topic.objects.get(name=topic_name)
        except Topic.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Topic not found'
            }, status=404)
        
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
            topic=topic,
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

def get_quiz_history(request):
    """
    Returns quiz history data in the format matching SAMPLE_QUIZZES from the frontend
    """
    try:
        # Get user_id from query parameters
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({
                'status': 'error',
                'message': 'user_id parameter is required'
            }, status=400)

        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User not found'
            }, status=404)

        # Get all quiz attempts for the specified user
        quiz_attempts = QuizAttempt.objects.filter(user=user).order_by('-created_at')
        
        quiz_history = []
        
        for attempt in quiz_attempts:
            # Get all question attempts for this quiz
            question_attempts = attempt.question_attempts.all()
            
            questions = []
            for q_attempt in question_attempts:
                question = q_attempt.question
                questions.append({
                    'question': question.question,
                    'options': question.options,
                    'correctAnswers': question.correct_answers,
                    'selectedAnswers': q_attempt.attempted_options,
                    'isCorrect': q_attempt.is_correct,
                    'partiallyCorrect': q_attempt.is_partial,
                    'timeTaken': q_attempt.time_taken,
                    'score': q_attempt.score,
                    'explanation': question.explanation
                })
            
            quiz_data = {
                'id': str(attempt.id),
                'topic': attempt.topic.name,  # Use topic name from Topic object
                'subtopic': attempt.subtopic,
                'date': attempt.created_at.strftime('%Y-%m-%d'),
                'percentage': attempt.score_percentage,
                'total_possible_score': attempt.total_possible_score,
                'score': attempt.score,
                'timeSpent': attempt.total_time_taken,
                'negativeMarking': attempt.is_negative_marking,
                'question_type': question_attempts.first().question.question_type,
                'questions': questions
            }
            
            quiz_history.append(quiz_data)
        
        return JsonResponse({
            'status': 'success',
            'quizzes': quiz_history
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)