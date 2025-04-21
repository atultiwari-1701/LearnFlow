# LearnFlow Backend

LearnFlow is a comprehensive learning platform that provides structured learning paths, resources, and quizzes for various technical topics.

## Repository
```bash
git clone https://github.com/atultiwari-1701/LearnFlow.git
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/atultiwari-1701/LearnFlow.git
cd LearnFlow
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv myenv
myenv\Scripts\activate

# Linux/Mac
python3 -m venv myenv
source myenv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
# Gemini API Keys
GEMINI_KEY_1=your_gemini_api_key1
GEMINI_KEY_2=your_gemini_api_key2

# YouTube API Keys
YOUTUBE_KEY_1=your_youtube_api_key1
YOUTUBE_KEY_2=your_youtube_api_key2
```

Then, update the `settings.py` file to include these keys:
```python
GEMINI_API_KEYS = [
    os.getenv('GEMINI_KEY_1'),
    os.getenv('GEMINI_KEY_2')
]

YOUTUBE_API_KEYS = [
    os.getenv('YOUTUBE_KEY_1'),
    os.getenv('YOUTUBE_KEY_2')
]
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## Running the Project

### Development Mode
1. Start the Django development server:
```bash
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`

2. For testing the API endpoints, you can use tools like:
   - Postman
   - cURL
   - Browser Developer Tools

### Production Mode
1. Set up a production web server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn LearnFlow.wsgi:application
```

2. Configure a reverse proxy (e.g., Nginx) to handle static files and SSL.

### Testing
Run the test suite:
```bash
python manage.py test
```

### Database Management
- Create migrations:
```bash
python manage.py makemigrations
```

- Apply migrations:
```bash
python manage.py migrate
```

- Create superuser (for admin access):
```bash
python manage.py createsuperuser
```

## API Endpoints

### Authentication

#### Sign Up
```http
POST /authentication/signup
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword",
    "name": "John Doe"  // Optional
}
```
Returns:
```json
{
    "status": "success",
    "message": "User created successfully",
    "user": {
        "id": "user_id",
        "email": "user@example.com",
        "name": "John Doe"
    }
}
```

#### Login
```http
POST /authentication/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword"
}
```
Returns:
```json
{
    "status": "success",
    "message": "Login successful",
    "user": {
        "id": "user_id",
        "email": "user@example.com",
        "name": "John Doe"
    }
}
```

### User Model
The User model includes the following fields:
- `id`: AutoField (primary key)
- `email`: EmailField (unique)
- `password`: CharField (hashed)
- `name`: CharField (optional)
- `created_at`: DateTimeField (auto_now_add)
- `updated_at`: DateTimeField (auto_now)

### Search and Topic Generation

#### Search for a Topic
```http
POST /gemini-search/search
Content-Type: application/json
X-Requested-With: XMLHttpRequest

{
    "search_query": "Python"
}
```
Returns comprehensive topic information including description, subtopics, roadmap, and more.

### Resource Generation

#### Generate Videos for Topic/Subtopic
```http
POST gemini-search/generate-topic-videos
Content-Type: application/json
X-Requested-With: XMLHttpRequest

{
    "topic_name": "Python",
    "subtopic_name": "Variables"  // Optional
}
```
Returns a list of relevant YouTube videos.

#### Generate Articles for Topic/Subtopic
```http
POST gemini-search/generate-topic-articles
Content-Type: application/json
X-Requested-With: XMLHttpRequest

{
    "topic_name": "Python",
    "subtopic_name": "Variables"  // Optional
}
```
Returns a list of relevant articles.

#### Generate Documentation for Topic/Subtopic
```http
POST gemini-search/generate-topic-documentation
Content-Type: application/json
X-Requested-With: XMLHttpRequest

{
    "topic_name": "Python",
    "subtopic_name": "Variables"  // Optional
}
```
Returns a list of relevant documentation sources.

### Quiz Management

#### Save Quiz Attempt
```http
POST /quiz/save-quiz-attempt
Content-Type: application/json

{
    "user_id": "user_id",
    "total_time_taken": 1200,  // in seconds
    "score": 32,
    "correct_attempts": 8,
    "incorrect_attempts": 2,
    "partial_attempts": 0,
    "unattempted": 0,
    "is_negative_marking": false,
    "topic": "Python",
    "subtopic": "Variables",
    "question_attempts": [
        {
            "question_id": 1,
            "time_taken": 45,
            "attempted_options": [0, 2]
        },
        // ... more question attempts
    ]
}
```
Saves a quiz attempt with detailed scoring and timing information.

#### Get Quiz History
```http
GET /quiz/quiz-history?user_id=<user_id>
```
Returns the user's quiz history with the following data for each quiz:
```json
{
    "status": "success",
    "quizzes": [
        {
            "id": "quiz_id",
            "topic": "Python",
            "subtopic": "Variables",
            "date": "2024-04-21",
            "percentage": 80.0,
            "total_possible_score": 40,
            "score": 32,
            "timeSpent": 1200,
            "negativeMarking": false,
            "question_type": "mcq",
            "questions": [
                {
                    "question": "What is a variable?",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correctAnswers": [0],
                    "selectedAnswers": [0],
                    "isCorrect": true,
                    "partiallyCorrect": false,
                    "timeTaken": 45,
                    "score": 4,
                    "explanation": "Variables are used to store data..."
                }
                // ... more questions
            ]
        }
        // ... more quizzes
    ]
}
```

### Quiz Scoring System

The quiz system uses the following scoring rules:

1. **Multiple Choice Questions (MCQ)**
   - Correct answer: +4 points
   - Incorrect answer with negative marking: -1 point
   - Incorrect answer without negative marking: 0 points
   - Unattempted: 0 points

2. **Multiple Correct Questions**
   - All correct options selected: +4 points
   - Partial correct (some correct options selected): +1 point per correct option
   - Incorrect options selected with negative marking: -2 points
   - Incorrect options selected without negative marking: 0 points
   - Unattempted: 0 points

3. **True/False Questions**
   - Correct answer: +4 points
   - Incorrect answer with negative marking: -1 point
   - Incorrect answer without negative marking: 0 points
   - Unattempted: 0 points

## Database Models

### Topic
- `name`: CharField (unique)
- `content`: TextField

### VideoResource
- `topic`: ForeignKey to Topic
- `subtopic`: CharField (optional)
- `title`: CharField
- `url`: URLField
- `duration`: CharField
- `thumbnail`: URLField

### ArticleResource
- `topic`: ForeignKey to Topic
- `subtopic`: CharField (optional)
- `title`: CharField
- `url`: URLField
- `read_time`: CharField

### DocumentationResource
- `topic`: ForeignKey to Topic
- `subtopic`: CharField (optional)
- `title`: CharField
- `url`: URLField
- `doc_type`: CharField

### QuizQuestion
- `topic`: ForeignKey to Topic
- `subtopic`: CharField (optional)
- `question_type`: CharField (choices: 'mcq', 'true-false', 'multiple-correct')
- `question`: TextField
- `options`: JSONField
- `correct_answers`: JSONField
- `explanation`: TextField

## Features

- Topic-based learning paths
- Subtopic-specific resources
- Multiple resource types (videos, articles, documentation)
- Quiz generation with different question types
- Database caching for faster responses
- Support for multiple API keys (Gemini, YouTube)
- Error handling and logging
- User authentication and authorization
- Quiz history tracking

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a message explaining the error:
```json
{
    "error": "Error message here"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Install development dependencies:
```bash
pip install -r requirements.txt
```
4. Make your changes
5. Run tests:
```bash
python manage.py test
```
6. Update dependencies (if you added new packages):
```bash
pip freeze > requirements.txt
```
7. Commit your changes
8. Push to the branch
9. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 