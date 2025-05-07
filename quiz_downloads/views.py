from django.shortcuts import render
from django.http import JsonResponse
import os
from .helpers import upload_file_to_supabase, get_cached_signed_url
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
    quiz_attempt_id = request.POST.get('quiz_attempt_id')

    if not quiz_file or not quiz_attempt_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Missing required fields'
        }, status=400)
    
    quiz_download, _ = QuizDownload.objects.get_or_create(quiz_attempt_id=quiz_attempt_id)
    
    # Extract the original filename and extension
    original_filename = quiz_file.name
    filename, file_extension = os.path.splitext(original_filename)
    if filename.endswith('questions'):
        file_path = f"quiz_downloads/{quiz_attempt_id}/questions/{original_filename}"
        if file_extension == '.txt':
            quiz_download.questions_txt = file_path
        elif file_extension == '.pdf':
            quiz_download.questions_pdf = file_path
    elif filename.endswith('answer_key'):
        file_path = f"quiz_downloads/{quiz_attempt_id}/answer_key/{original_filename}"
        if file_extension == '.txt':
            quiz_download.answers_txt = file_path
        elif file_extension == '.pdf':
            quiz_download.answers_pdf = file_path
    elif filename.endswith('attempts_and_answers'):
        file_path = f"quiz_downloads/{quiz_attempt_id}/attempts_and_answers/{original_filename}"
        if file_extension == '.txt':
            quiz_download.user_attempt_txt = file_path
        elif file_extension == '.pdf':
            quiz_download.user_attempt_pdf = file_path
    elif filename.endswith('report_card'):
        import io
        import zipfile
        # Prepare zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add the uploaded file to the zip
            zip_file.writestr(original_filename, quiz_file.read())
        zip_buffer.seek(0)
        # Name for the zip file
        zip_filename = f"{filename}.zip"
        file_path = f"quiz_downloads/{quiz_attempt_id}/report_card/{zip_filename}"
        quiz_download.report_pdf = file_path
        # Prepare file-like object for upload
        class InMemoryUploadedFile(io.BytesIO):
            def __init__(self, buf, name):
                super().__init__(buf.getvalue())
                self.name = name
        quiz_file = InMemoryUploadedFile(zip_buffer, zip_filename)

    try:
        upload_file_to_supabase(quiz_file, file_path)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Upload failed: {str(e)}'
        }, status=500)
    
    quiz_download.save()

    return JsonResponse({
        'status': 'success',
        'message': 'File uploaded successfully',
        'file_path': file_path
    })
