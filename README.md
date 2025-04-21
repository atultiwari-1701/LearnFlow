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
POST /auth/signup
Content-Type: application/json

{
    "username": "user123",
    "email": "user@example.com",
    "password": "securepassword"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
    "username": "user123",
    "password": "securepassword"
}
```

### Search and Topic Generation

#### Search for a Topic
```http
POST /search
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
POST /generate-topic-videos
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
POST /generate-topic-articles
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
POST /generate-topic-documentation
Content-Type: application/json
X-Requested-With: XMLHttpRequest

{
    "topic_name": "Python",
    "subtopic_name": "Variables"  // Optional
}
```
Returns a list of relevant documentation sources.

### Quiz Management

#### Generate Quiz
```http
POST /generate-quiz
Content-Type: application/json

{
    "topic": "Python",
    "subtopic": "Variables",  // Optional
    "question_type": "mcq",   // Options: "mcq", "true-false", "multiple-correct"
    "num_questions": 10       // Optional, default: 10
}
```
Returns a quiz with the specified number of questions.

#### Get User's Quiz History
```http
GET /quiz/history
Authorization: Bearer <token>

{
    "page": 1,           // Optional, default: 1
    "page_size": 10      // Optional, default: 10
}
```
Returns the user's quiz history with pagination.

#### Get Quiz Results
```http
GET /quiz/results/{quiz_id}
Authorization: Bearer <token>
```
Returns detailed results for a specific quiz.

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