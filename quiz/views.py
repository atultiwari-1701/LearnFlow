import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import QuizAttempt, QuestionAttempt
from search_app.models import QuizQuestion, Topic
from django.core.serializers.json import DjangoJSONEncoder
from authentication.models import User

# Create your views here.
from django.core.paginator import Paginator

# --- View: Quiz Stats for Profile Page ---
def get_quiz_stats(request):
    """
    Returns all quiz statistics for the currently logged-in user, matching the calculations in the ProfilePage frontend.
    Optimized for performance and scalability.
    """
    if request.session.get('user_id') is None:
        return JsonResponse({
            'status': 'error',
            'message': 'User not logged in'
        }, status=401)
    try:
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
        # Avoid N+1 queries: fetch all related objects in one go
        quiz_attempts = (
            QuizAttempt.objects
            .filter(user=user)
            .select_related('topic')
            .prefetch_related(
                'question_attempts__question'
            )
            .order_by('created_at')  # ascending for score progression
        )
        # Prepare all stats in a single pass
        topic_stats = {}
        question_type_stats = {}
        score_distribution = {}
        time_analysis = []
        performance_by_qtype = {}
        score_progression = []
        cumulative_sum = 0
        quiz_count_by_qtype = {}
        quizzes_for_progression = []  # store (date, score, topic) for progression
        # --- Stats for summary ---
        total_quizzes = 0
        total_percentage = 0
        topic_set = set()
        total_time_spent = 0
        for idx, attempt in enumerate(quiz_attempts):
            topic_name = attempt.topic.name
            created_at_str = attempt.created_at.strftime('%Y-%m-%d')
            question_attempts = list(attempt.question_attempts.all())
            # Defensive: skip quiz if it has no question attempts
            if not question_attempts:
                continue
            first_question = question_attempts[0].question
            question_type = first_question.question_type if first_question else ''
            # Calculate score and stats for this quiz
            questions = []
            correct_count = 0
            for q_attempt in question_attempts:
                q = q_attempt.question
                is_correct = q_attempt.is_correct
                correct_count += 1 if is_correct else 0
                questions.append({
                    'question': q.question,
                    'options': q.options,
                    'correctAnswers': q.correct_answers,
                    'selectedAnswers': q_attempt.attempted_options,
                    'isCorrect': is_correct,
                    'partiallyCorrect': q_attempt.is_partial,
                    'timeTaken': q_attempt.time_taken,
                    'score': q_attempt.score,
                    'explanation': q.explanation
                })
            total_score = sum(q['score'] for q in questions)
            total_possible_score = attempt.total_possible_score
            percentage = round((total_score / total_possible_score) * 100, 2) if total_possible_score > 0 else 0
            # --- summary stats ---
            total_quizzes += 1
            total_percentage += percentage
            topic_set.add(topic_name)
            total_time_spent += attempt.total_time_taken
            # --- topicStats ---
            if topic_name not in topic_stats:
                topic_stats[topic_name] = {
                    'name': topic_name,
                    'quizzes': 0,
                    'avgScore': 0,
                    'totalScore': 0,
                    'questionTypes': {'mcq': 0, 'multiple-correct': 0, 'true-false': 0}
                }
            topic_stats[topic_name]['quizzes'] += 1
            topic_stats[topic_name]['totalScore'] += total_score
            topic_stats[topic_name]['avgScore'] = round(topic_stats[topic_name]['totalScore'] / topic_stats[topic_name]['quizzes'])
            if question_type in topic_stats[topic_name]['questionTypes']:
                topic_stats[topic_name]['questionTypes'][question_type] += 1
            # --- questionTypeData ---
            question_type_stats[question_type] = question_type_stats.get(question_type, 0) + 1
            quiz_count_by_qtype[question_type] = quiz_count_by_qtype.get(question_type, 0) + 1
            # --- scoreDistributionData ---
            rng = int(total_score // 10) * 10
            key = f"{rng}-{rng+9}"
            score_distribution[key] = score_distribution.get(key, 0) + 1
            # --- timeAnalysis ---
            def seconds_to_minutes(seconds):
                return seconds / 60 if seconds else 0
            time_analysis.append({
                'topic': topic_name,
                'timeInMinutes': seconds_to_minutes(attempt.total_time_taken),
                'score': percentage
            })
            # --- performanceByQuestionTypeData ---
            if question_type not in performance_by_qtype:
                performance_by_qtype[question_type] = {'totalQuestions': 0, 'correctAnswers': 0, 'time': 0}
            performance_by_qtype[question_type]['totalQuestions'] += len(questions)
            performance_by_qtype[question_type]['correctAnswers'] += correct_count
            performance_by_qtype[question_type]['time'] += attempt.total_time_taken
            # --- scoreProgression ---
            quizzes_for_progression.append((created_at_str, total_score, topic_name))
        # Prepare topicStats array
        topic_stats_array = list(topic_stats.values())
        # Prepare questionTypeData
        question_type_data = [{'name': k, 'value': v} for k, v in question_type_stats.items()]
        # Prepare scoreDistributionData
        score_distribution_data = [{'range': k, 'count': v} for k, v in score_distribution.items()]
        # Prepare performanceByQuestionTypeData
        performance_by_qtype_data = []
        for qtype, data in performance_by_qtype.items():
            count = quiz_count_by_qtype.get(qtype, 1)
            avg_time = (data['time'] / count) / 60 if count > 0 else 0
            accuracy = (data['correctAnswers'] / data['totalQuestions']) * 100 if data['totalQuestions'] > 0 else 0
            performance_by_qtype_data.append({
                'type': qtype,
                'accuracy': accuracy,
                'avgTime': avg_time
            })
        # Prepare scoreProgression
        score_progression = []
        cumulative_sum = 0
        for idx, (date, score, topic) in enumerate(sorted(quizzes_for_progression, key=lambda x: x[0])):
            cumulative_sum += score
            score_progression.append({
                'date': date,
                'score': score,
                'topic': topic,
                'cumulativeAvg': cumulative_sum / (idx + 1)
            })
        average_score = round(total_percentage / total_quizzes, 2) if total_quizzes > 0 else None
        total_topics = len(topic_set)
        return JsonResponse({
            'status': 'success',
            'topicStats': topic_stats_array,
            'questionTypeData': question_type_data,
            'scoreDistributionData': score_distribution_data,
            'timeAnalysis': time_analysis,
            'performanceByQuestionTypeData': performance_by_qtype_data,
            'scoreProgression': score_progression,
            'averageScore': average_score,
            'totalQuizzes': total_quizzes,
            'totalTopics': total_topics,
            'totalTimeSpent': total_time_spent
        }, encoder=DjangoJSONEncoder)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

# --- View 1: Paginated Topics ---

# --- View 3: Paginated Questions for Quiz Attempt ---
def get_questions_for_quiz_attempt(request, quiz_attempt_id):
    """
    Returns paginated questions (5 per page) for a given quiz attempt and current user.
    Query param: page (default=1)
    """
    if request.session.get('user_id') is None:
        return JsonResponse({
            'status': 'error',
            'message': 'User not logged in'
        }, status=401)
    try:
        page_number = int(request.GET.get('page', 1))
        if page_number < 1:
            page_number = 1
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
        # Validate quiz attempt
        try:
            quiz_attempt = QuizAttempt.objects.get(id=quiz_attempt_id, user=user)
        except QuizAttempt.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Quiz attempt not found'}, status=404)
        question_attempts = quiz_attempt.question_attempts.all()
        paginator = Paginator(question_attempts, 5)
        page = paginator.get_page(page_number)
        questions_data = []
        for q_attempt in page.object_list:
            question = q_attempt.question
            questions_data.append({
                'id': question.id,
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
        return JsonResponse({
            'status': 'success',
            'questions': questions_data,
            'page': page_number,
            'num_pages': paginator.num_pages,
            'total_questions': paginator.count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def get_topics_paginated(request):
    """
    Returns paginated list of topics (9 per page)
    Query param: page (default=1)
    """
    if request.session.get('user_id') is None:
        return JsonResponse({
            'status': 'error',
            'message': 'User not logged in'
        }, status=401)

    try:
        page_number = int(request.GET.get('page', 1))
        if page_number < 1:
            page_number = 1
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
        # Get unique topics for which the user has at least one QuizAttempt
        topic_ids = QuizAttempt.objects.filter(user=user).values_list('topic_id', flat=True).distinct()
        topics = Topic.objects.filter(id__in=topic_ids)
        paginator = Paginator(topics, 9)
        page = paginator.get_page(page_number)
        topics_data = [
            {
                'id': topic.id,
                'name': topic.name,
                'quiz_count': QuizAttempt.objects.filter(user=user, topic=topic).count()
            }
            for topic in page.object_list
        ]
        return JsonResponse({
            'status': 'success',
            'topics': topics_data,
            'page': page_number,
            'num_pages': paginator.num_pages,
            'total_topics': paginator.count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

# --- View 2: Paginated Quizzes for Topic ---
def get_quizzes_for_topic(request, topic_id):
    """
    Returns paginated quizzes for a specific topic (4 per page)
    Query param: page (default=1)
    """
    if request.session.get('user_id') is None:
        return JsonResponse({
            'status': 'error',
            'message': 'User not logged in'
        }, status=401)
    try:
        page_number = int(request.GET.get('page', 1))
        if page_number < 1:
            page_number = 1
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
        # Validate topic
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Topic not found'}, status=404)
        quizzes = QuizAttempt.objects.filter(user=user, topic=topic).order_by('-created_at')
        paginator = Paginator(quizzes, 5)
        page = paginator.get_page(page_number)
        quiz_history = []
        for attempt in page.object_list:
            quiz_data = {
                'id': str(attempt.id),
                'topic': attempt.topic.name,
                'subtopic': attempt.subtopic,
                'date': attempt.created_at.strftime('%Y-%m-%d'),
                'timeSpent': attempt.total_time_taken,
                'percentage': attempt.score_percentage
            }
            quiz_history.append(quiz_data)
        return JsonResponse({
            'status': 'success',
            'quizzes': quiz_history,
            'page': page_number,
            'num_pages': paginator.num_pages,
            'total_quizzes': paginator.count
        }, encoder=DjangoJSONEncoder)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def save_quiz_attempt(request):
    if request.session.get('user_id') is None:
        return JsonResponse({
            'status': 'error',
            'message': 'User not logged in'
        }, status=401)
    # Check if request method is POST
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['total_time_taken', 'correct_attempts', 
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
            user_id=request.session.get('user_id'),  # Assuming user_id is stored in session
            total_time_taken=data['total_time_taken'],
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
    if request.session.get('user_id') is None:
        return JsonResponse({
            'status': 'error',
            'message': 'User not logged in'
        }, status=401)

    try:
        # Get user_id from query parameters
        user_id = request.session.get('user_id')
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