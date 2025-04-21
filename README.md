# LearnFlow Backend

LearnFlow is a comprehensive learning platform that provides structured learning paths, resources, and quizzes for various technical topics.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
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
GEMINI_API_KEYS=your_gemini_api_key1,your_gemini_api_key2
YOUTUBE_API_KEYS=your_youtube_api_key1,your_youtube_api_key2
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

## API Endpoints

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

### Quiz Generation

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

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
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
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 