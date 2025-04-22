import os
import json
import traceback
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from google import genai
from google.genai import types
from .youtube_api import search_youtube
import logging
import random
from .models import QuizQuestion, Topic, VideoResource, ArticleResource, DocumentationResource
from itertools import cycle
from django.db import transaction

_gemini_api_key_cycle = cycle(settings.GEMINI_API_KEYS)
_youtube_api_key_cycle = cycle(settings.YOUTUBE_API_KEYS)

# Configure logging (optional, for debugging)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def call_gemini_model(prompt, model_name="gemini-2.0-pro-exp-02-05", temperature=1, top_p=0.95, top_k=64, max_output_tokens=8192, response_mime_type="application/json"):
    """
    Calls the Gemini model with the given prompt and configuration.
    """
    try:
        client = genai.Client(api_key=next(_gemini_api_key_cycle))
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type,
        )
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        )
        return response.text
    except Exception as e:
        logging.error(f"Error calling Gemini model: {e}")
        traceback.print_exc()
        raise e

def generate_prompt(topic):
    prompt_template = """
        {topic-name} = {topic}
Replace the value of {topic-name} in the output object.

Gather the following information about the topic {topic-name}.

Output a single valid JSON object inside the response with key as {topic} and another key as "topic" and its value to be the {topic-name} for example {"topic": "Python", "Python": {rest as shown below}}. The JSON object should contain the following keys and values:

{
    "Short Description": {
        "Description": "Write a concise description between 100 and 120 words, using a friendly and conversational tone that encourages beginners. Highlight key points using **bold** text. **Example for 'Python':** **Python** is a versatile language known for its readability. It's used in web development, data science, and more." 
    },
    "Need to Learn {topic-name}": {
        "Description": "Explain in a maximum of 50 words why learning {topic-name} is valuable. Use a motivating, beginner-friendly tone. **Example for 'Python':** Learning Python opens doors to exciting career opportunities and empowers you to build innovative applications.",
        "Benefit 1": {"heading": "give breif heading in 1 or 2 words", "description": "give breif description in 20-30 words"},
        "Benefit 2": {"heading": "give breif heading in 1 or 2 words", "description": "give breif description in 20-30 words"},
        "Benefit 3": {"heading": "give breif heading in 1 or 2 words", "description": "give breif description in 20-30 words"},
    },
    "Resource Tab Suggestions": {
        "Description": "Provide 3 resource tab name suggestions that would be most helpful for learning {topic-name}. Strictly select from the following options: 'Videos', 'Articles', 'Courses', 'Books', 'Documentation','Cheat Sheets','Practice Problems'. **Example for 'Python':** ['Videos', 'Documentations', 'Practice Problems']" 
    },
    "SubTopics": {
        "Description": {
            "subtopics": [
                {
                    "name": "give name of subtopic here",
                    "description": "40-50 word description. **Example for 'Python Variables':** Understanding how to store and manipulate data.",
                    "difficulty": "Beginner, Intermediate, Advanced, Expert, Mastery. **Example for 'Python Variables':** Beginner",
                    "timeToComplete": "e.g., 2 hours. **Example for 'Python Variables':** 2 hours",
                    "whyItMatters": "20-30 word explanation. **Example for 'Python Variables':** Fundamental for all Python programming tasks.",
                    "commonMistakes": [
                        "**Example for 'Python Variables':** Using incorrect data types.",
                        "**Example for 'Python Variables':** Not understanding variable scope.",
                        "**Example for 'Python Variables':** Naming variables poorly."
                    ],
                    resourceTabs: [],          
                },
                {
                    "name": "give name of subtopic here",
                    "description": "40-50 word description. **Example for 'Python Loops':** Learning to control program flow.",
                    "difficulty": "Beginner, Intermediate, Advanced, Expert, Mastery. **Example for 'Python Loops':** Intermediate",
                    "timeToComplete": "e.g., 2 hours. **Example for 'Python Loops':** 3 hours",
                    "whyItMatters": "20-30 word explanation. **Example for 'Python Loops':** Enables you to write efficient code.",
                    "commonMistakes": [
                        "**Example for 'Python Loops':** Incorrect loop conditions.",
                        "**Example for 'Python Loops':** Not handling edge cases.",
                        "**Example for 'Python Loops':** Using infinite loops."
                    ],
                    resourceTabs: [],          
                },
                // Add more subtopics as needed (At least 6 subtopics are required)
            ]
        }
    },
    "Road Map to Learn {topic-name}": {
        "Description": {
            "prerequisites": {
                ["An array to detail all the prerequisites for learning {topic-name}. Include at least 3 prerequisites.",]
            },
            "levels": [
                {
                    "name": "Basic Level", // must be "Basic Level" if basic level exists
                    "description": "Give basic description in 3-5 words of what this level contains",
                    "topics": [
                        "**Example for 'Python':** Setting up Python environment.",
                        "**Example for 'Python':** Basic syntax.",
                        "**Example for 'Python':** Simple programs."
                    ],
                    "howToConquer": "Actionable advice. **Example for 'Python':** Practice coding exercises.",
                    "insiderTips": "50-word tips. **Example for 'Python':** Join online communities."
                },
                {
                    "name": "Intermediate Level", // must be "Intermediate Level" if Intermediate level exists
                    "description": "Give basic description in 3-5 words of what this level contains",
                    "topics": [
                        "**Example for 'Python':** Object-oriented programming.",
                        "**Example for 'Python':** Working with APIs.",
                        "**Example for 'Python':** Web applications."
                    ],
                    "howToConquer": "Actionable advice. **Example for 'Python':** Build personal projects.",
                    "insiderTips": "50-word tips. **Example for 'Python':** Focus on readability."
                },
                {
                    "name": "Advanced Level", // must be "Advanced Level" if Advanced level exists
                    "description": "Give basic description in 3-5 words of what this level contains",
                    "topics": [
                        "**Example for 'Python':** Data analysis.",
                        "**Example for 'Python':** Machine learning.",
                        "**Example for 'Python':** Advanced libraries."
                    ],
                    "howToConquer": "Actionable advice. **Example for 'Python':** Contribute to open-source.",
                    "insiderTips": "50-word tips. **Example for 'Python':** Stay updated with trends."
                },
                {
                    "name": "Expert Level", // must be "Expert Level" if Expert level exists
                    "description": "Give basic description in 3-5 words of what this level contains",
                    "topics": [
                        "**Example for 'Python':** Performance optimization.",
                        "**Example for 'Python':** Advanced algorithms.",
                        "**Example for 'Python':** System design."
                    ],
                    "howToConquer": "Actionable advice. **Example for 'Python':** Mentor others.",
                    "insiderTips": "50-word tips. **Example for 'Python':** Network with professionals."
                },
                // At least 3 levels are required
            ]
        }
    },
    "Key Takeaways": {
        "Description": "A JSON array containing 3-5 impactful takeaways in detail that summarize the most important points of learning {topic-name}. Each takeaway should be a short, direct statement. **Example for 'Python':** ['Python is versatile and beginner-friendly.', 'Practice is essential to mastering Python.', 'Python has a rich ecosystem of libraries.', 'Python is used in web development, data science, and automation.', 'Python promotes code readability and maintainability.']"
    },
    "Frequently Asked Questions": {
        "Description": [
            {
                "question": "Example for 'Python': What is Python used for?",
                "answer": "Example for 'Python': Web development."
            },
            {
                "question": "Example for 'Python': How to install Python?",
                "answer": "Example for 'Python': Download from website."
            },
            // Add more FAQs as needed (at least 5 FAQs are required)
        ]
    },
    "Related Topics": {
        "Description": [
            {
                "topic": "Example for 'Python': Web Development",
                "description": "Example for 'Python': Building websites."
            },
            {
                "topic": "Example for 'Python': Data Science",
                "description": "Example for 'Python': Analyzing data."
            },
            // Add more related topics as needed (at least 3 related topics are required)
        ]
    }
}
    """
    return prompt_template.replace("{topic}", topic)

def search_gemini(request):
    print("search_gemini called")
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("it is a post request")
        topic_name = json.loads(request.body).get('search_query', '')
        print(f"topic_name: {topic_name}")
        
        try:
            # Check if topic already exists
            topic = Topic.objects.filter(name=topic_name).first()
            if topic:
                # Return existing content if available
                return JsonResponse({'result': topic.content})
            
            # Generate new content if topic doesn't exist
            prompt = generate_prompt(topic_name)
            result = call_gemini_model(prompt)
            
            # Create new topic with generated content
            Topic.objects.create(name=topic_name, content=result)
            
            return JsonResponse({'result': result})
            
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def generate_quiz(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        topic_name = data.get('topic')
        subtopic = data.get('subtopic', '')
        question_type = data.get('question_type', 'mcq')
        num_questions = data.get('num_questions', 10)
        
        # Get or create the Topic object
        try:
            topic = Topic.objects.get(name=topic_name)
        except Topic.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Topic not found'
            }, status=404)
        
        # 50-50 chance to use database or Gemini
        use_database = random.choice([True, False])
        
        if use_database:
            # Try to get questions from database first
            questions = QuizQuestion.objects.filter(
                topic=topic,
                subtopic=subtopic,
                question_type=question_type
            )
            
            if questions.exists():
                # If we have questions in database, use them
                if questions.count() >= num_questions:
                    # If we have enough questions, randomly select from existing ones
                    selected_questions = random.sample(list(questions), num_questions)
                    questions_data = []
                    for q in selected_questions:
                        questions_data.append({
                            'id': q.id,
                            'question': q.question,
                            'options': q.options,
                            'correct_answers': q.correct_answers,
                            'explanation': q.explanation,
                            'type': q.question_type
                        })
                    return JsonResponse({'quiz': {'quiz': questions_data}})
                else:
                    # If we don't have enough questions, fall back to Gemini
                    logger.info(f"Database has {questions.count()} questions, falling back to Gemini for {num_questions} questions")
                    use_database = False
        
        if not use_database:
            # Generate new questions using Gemini
            prompt = f"""
                Create a quiz on the {'subtopic of ' + subtopic + ' within the broader topic of ' if subtopic else 'topic of '}{topic_name}. 
                The quiz should consist of {num_questions} questions. 
                All questions should be of type '{question_type}'.
                There should be only 4 options for mcq type and multiple-correct type questions and only 2 options for true-false type questions.
                For each question, provide:
                    type: string;
                    question: string;
                    options: string[];
                    correct_answers: number[];
                    explanation: string;
                
                Return the quiz in JSON format with a "quiz" key containing an array of questions.
            """
            
            response_text = call_gemini_model(prompt)
            quiz_data = eval(response_text)
            
            # Store new questions in database and collect their IDs
            final_questions = []
            with transaction.atomic():
                for question in quiz_data["quiz"]:
                    try:
                        # Check if question already exists
                        existing_question = QuizQuestion.objects.filter(
                            topic=topic,
                            subtopic=subtopic,
                            question_type=question_type,
                            question=question["question"]
                        ).first()

                        if existing_question:
                            # Use existing question with its ID
                            final_questions.append({
                                "id": existing_question.id,
                                "type": existing_question.question_type,
                                "question": existing_question.question,
                                "options": existing_question.options,
                                "correct_answers": existing_question.correct_answers,
                                "explanation": existing_question.explanation
                            })
                        else:
                            # Create new question and get its ID
                            new_question = QuizQuestion.objects.create(
                                topic=topic,
                                subtopic=subtopic,
                                question_type=question_type,
                                question=question["question"],
                                options=question["options"],
                                correct_answers=question["correct_answers"],
                                explanation=question["explanation"],
                                source="gemini"
                            )
                            final_questions.append({
                                "id": new_question.id,
                                "type": new_question.question_type,
                                "question": new_question.question,
                                "options": new_question.options,
                                "correct_answers": new_question.correct_answers,
                                "explanation": new_question.explanation
                            })
                    except Exception as e:
                        logger.warning(f"Error processing question: {e}")
                        continue
            
            return JsonResponse({'quiz': {"quiz": final_questions}})

    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return JsonResponse({'error': str(e)}, status=400)

def generate_videos_for_topic(request):
    """Generate YouTube videos for a specific topic or subtopic."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            topic_name = data.get('topic_name', '')
            subtopic_name = data.get('subtopic_name', '')
            
            if not topic_name:
                return JsonResponse({'error': 'Topic name is required'}, status=400)
            
            # Get or create the Topic object
            topic, _ = Topic.objects.get_or_create(name=topic_name)
            
            # Check if videos already exist in database
            existing_videos = VideoResource.objects.filter(
                topic=topic,
                subtopic=subtopic_name if subtopic_name else ''
            )
            
            if existing_videos.exists():
                videos = [{
                    'title': video.title,
                    'url': video.url,
                    'duration': video.duration,
                    'thumbnail': video.thumbnail
                } for video in existing_videos]
                return JsonResponse({'videos': videos})
            
            # Generate new videos if not in database
            youtube_prompt = f"{f'{topic_name} {subtopic_name}' if subtopic_name else topic_name} tutorial"
            youtube_results = search_youtube(next(_youtube_api_key_cycle), youtube_prompt)
            
            videos = []
            if youtube_results:
                with transaction.atomic():
                    for video in youtube_results[:2]:  # Get top 2 videos
                        video_url = video.get('url', '')
                        video_id = video_url.split('v=')[-1] if 'v=' in video_url else ''
                        
                        video_data = {
                            'title': video.get('title', ''),
                            'url': video_url,
                            'duration': video.get('duration', ''),
                            'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" if video_id else ''
                        }
                        
                        # Save to database
                        VideoResource.objects.create(
                            topic=topic,
                            subtopic=subtopic_name if subtopic_name else '',
                            **video_data
                        )
                        
                        videos.append(video_data)
            
            return JsonResponse({'videos': videos})
            
        except Exception as e:
            logger.error(f"Error generating videos: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def generate_articles_for_topic(request):
    """Generate articles for a specific topic or subtopic."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            topic_name = data.get('topic_name', '')
            subtopic_name = data.get('subtopic_name', '')
            
            if not topic_name:
                return JsonResponse({'error': 'Topic name is required'}, status=400)
            
            # Get or create the Topic object
            topic, _ = Topic.objects.get_or_create(name=topic_name)
            
            # Check if articles already exist in database
            existing_articles = ArticleResource.objects.filter(
                topic=topic,
                subtopic=subtopic_name if subtopic_name else ''
            )
            
            if existing_articles.exists():
                articles = [{
                    'title': article.title,
                    'url': article.url,
                    'readTime': article.read_time
                } for article in existing_articles]
                return JsonResponse({'articles': articles})
            
            # Generate new articles if not in database
            gemini_prompt = f"""
                Generate 2 high-quality, beginner-friendly articles about {f'{topic_name} {subtopic_name}' if subtopic_name else topic_name}.
                Return a JSON array with the following structure for each article:
                {{
                    "title": "article title",
                    "url": "article url",
                    "readTime": "estimated read time"
                }}
                
                Make sure all URLs are valid and accessible.
            """
            
            gemini_response = call_gemini_model(gemini_prompt)
            articles_data = json.loads(gemini_response)
            
            # Save to database
            articles = []
            with transaction.atomic():
                for article_data in articles_data:
                    article = ArticleResource.objects.create(
                        topic=topic,
                        subtopic=subtopic_name if subtopic_name else '',
                        title=article_data['title'],
                        url=article_data['url'],
                        read_time=article_data['readTime']
                    )
                    articles.append({
                        'title': article.title,
                        'url': article.url,
                        'readTime': article.read_time
                    })
            
            return JsonResponse({'articles': articles})
            
        except Exception as e:
            logger.error(f"Error generating articles: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def generate_documentation_for_topic(request):
    """Generate documentation for a specific topic or subtopic."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            topic_name = data.get('topic_name', '')
            subtopic_name = data.get('subtopic_name', '')
            
            if not topic_name:
                return JsonResponse({'error': 'Topic name is required'}, status=400)
            
            # Get or create the Topic object
            topic, _ = Topic.objects.get_or_create(name=topic_name)
            
            # Check if documentation already exists in database
            existing_docs = DocumentationResource.objects.filter(
                topic=topic,
                subtopic=subtopic_name if subtopic_name else ''
            )
            
            if existing_docs.exists():
                documentation = [{
                    'title': doc.title,
                    'url': doc.url,
                    'type': doc.doc_type
                } for doc in existing_docs]
                return JsonResponse({'documentation': documentation})
            
            # Generate new documentation if not in database
            gemini_prompt = f"""
                Generate 2 official or widely recognized documentation sources for {f'{topic_name} {subtopic_name}' if subtopic_name else topic_name}.
                Return a JSON array with the following structure for each documentation:
                {{
                    "title": "documentation title",
                    "url": "documentation url",
                    "type": "documentation type"
                }}
                
                Make sure all URLs are valid and accessible.
            """
            
            gemini_response = call_gemini_model(gemini_prompt)
            docs_data = json.loads(gemini_response)
            
            # Save to database
            documentation = []
            with transaction.atomic():
                for doc_data in docs_data:
                    doc = DocumentationResource.objects.create(
                        topic=topic,
                        subtopic=subtopic_name if subtopic_name else '',
                        title=doc_data['title'],
                        url=doc_data['url'],
                        doc_type=doc_data['type']
                    )
                    documentation.append({
                        'title': doc.title,
                        'url': doc.url,
                        'type': doc.doc_type
                    })
            
            return JsonResponse({'documentation': documentation})
            
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)