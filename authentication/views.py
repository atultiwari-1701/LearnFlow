import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

# Create your views here.
def signup(request):
    """Handles user signup."""
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        password = data.get('password')
        email = data.get('email', '')
        if not name or not password or not email:
            return JsonResponse({'error': 'Email, Username and password are required.'}, status=400)
        try:
            password = make_password(password)
            user: User = User(name=name, email=email, password=password)
            user.save()
            return JsonResponse({'message': 'User created successfully.', 'user': {'email': user.email, 'name': user.name, 'id': user.pk}})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def login_view(request):
    """Handles user login."""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=400)
        try:
            user: User = User.objects.get(email=email)
            if check_password(password, user.password):
                return JsonResponse({'message': 'Login successful.', 'user': {'email': user.email, 'name': user.name, 'id': user.pk}})
            else:
                return JsonResponse({'error': 'Invalid email or password'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)