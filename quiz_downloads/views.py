from django.shortcuts import render
from django.http import JsonResponse
import os
from .helpers import upload_file_to_supabase
from .models import QuizDownload

# Create your views here.
def store_quiz_download_files(request):
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
    
    # Get file and quiz attempt ID from POST data
    quiz_file = request.FILES.get('file')
    quiz_attempt_id = int(request.POST.get('quiz_attempt_id'))

    if not quiz_file or not quiz_attempt_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Missing required fields'
        }, status=400)
    
    quiz_download, _ = QuizDownload.objects.get_or_create(quiz_attempt_id=quiz_attempt_id)
    
    update_fields = {}

    # Extract the original filename and extension
    original_filename = quiz_file.name
    filename, file_extension = os.path.splitext(original_filename)
    if filename.endswith('questions'):
        file_path = f"quiz_downloads/{quiz_attempt_id}/questions/{original_filename}"
        if file_extension == '.txt':
            update_fields['questions_txt'] = file_path
        elif file_extension == '.pdf':
            update_fields['questions_pdf'] = file_path
    elif filename.endswith('answer_key'):
        file_path = f"quiz_downloads/{quiz_attempt_id}/answer_key/{original_filename}"
        if file_extension == '.txt':
            update_fields['answers_txt'] = file_path
        elif file_extension == '.pdf':
            update_fields['answers_pdf'] = file_path
    elif filename.endswith('attempts_and_answers'):
        file_path = f"quiz_downloads/{quiz_attempt_id}/attempts_and_answers/{original_filename}"
        if file_extension == '.txt':
            update_fields['user_attempt_txt'] = file_path
        elif file_extension == '.pdf':
            update_fields['user_attempt_pdf'] = file_path
    elif filename.endswith('report_card'):
        file_path = f"quiz_downloads/{quiz_attempt_id}/report_card/{original_filename}"
        update_fields['report_pdf'] = file_path
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid file type'
        }, status=400)

    try:
        supabase_index = upload_file_to_supabase(quiz_file, file_path)
        if quiz_download.storage_index != supabase_index:
            update_fields['storage_index'] = supabase_index
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Upload failed: {str(e)}'
        }, status=500)
    
    QuizDownload.objects.filter(quiz_attempt_id=quiz_attempt_id).update(**update_fields)

    return JsonResponse({
        'status': 'success',
        'message': 'File uploaded successfully',
        'file_path': file_path
    })
