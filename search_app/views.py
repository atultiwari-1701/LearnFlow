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
from .models import QuizQuestion
from itertools import cycle

_gemini_api_key_cycle = cycle(settings.GEMINI_API_KEYS)
_youtube_api_key_cycle = cycle(settings.YOUTUBE_API_KEYS)

# Configure logging (optional, for debugging)
logging.basicConfig(level=logging.DEBUG)

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
                    "name": "Basic Level",
                    "topics": [
                        "**Example for 'Python':** Setting up Python environment.",
                        "**Example for 'Python':** Basic syntax.",
                        "**Example for 'Python':** Simple programs."
                    ],
                    "howToConquer": "Actionable advice. **Example for 'Python':** Practice coding exercises.",
                    "insiderTips": "50-word tips. **Example for 'Python':** Join online communities."
                },
                {
                    "name": "Intermediate Level",
                    "topics": [
                        "**Example for 'Python':** Object-oriented programming.",
                        "**Example for 'Python':** Working with APIs.",
                        "**Example for 'Python':** Web applications."
                    ],
                    "howToConquer": "Actionable advice. **Example for 'Python':** Build personal projects.",
                    "insiderTips": "50-word tips. **Example for 'Python':** Focus on readability."
                },
                {
                    "name": "Advanced Level",
                    "topics": [
                        "**Example for 'Python':** Data analysis.",
                        "**Example for 'Python':** Machine learning.",
                        "**Example for 'Python':** Advanced libraries."
                    ],
                    "howToConquer": "Actionable advice. **Example for 'Python':** Contribute to open-source.",
                    "insiderTips": "50-word tips. **Example for 'Python':** Stay updated with trends."
                },
                {
                    "name": "Expert Level",
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

from .models import Topic

def search_gemini(request):
    print("search_gemini called")
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("it is a post request")
        topic_name = json.loads(request.body).get('search_query', '')
        print(f"topic_name: {topic_name}")

        if Topic.objects.filter(name=topic_name).exists():
            print(f"Topic '{topic_name}' already exists in the database.")
            topic = Topic.objects.get(name=topic_name)
            response_text = topic.content
            return JsonResponse({'result': response_text})

        if topic_name:
            try:
                prompt = generate_prompt(topic_name)
                response_text = call_gemini_model(prompt)
                # Save the response_text in the Topics model
                topic = Topic(name=topic_name, content=response_text)
                topic.save()
                print("Gemini API call successful")
                return JsonResponse({'result': response_text})
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                return JsonResponse({'error': str(e)}, status=500)
        else:
            print("Search query empty")
            return JsonResponse({'error': 'Search query is empty.'}, status=400)
    print("search page rendered")
    return render(request, 'search.html')

def generate_resources(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        prompt =request.POST.get('prompt')
        print(f"Prompt: {prompt}")

        try:
            response_text = call_gemini_model(prompt)
            print(response_text) # add this line
            return JsonResponse({'result': response_text})
        except Exception as e:
            print(e) # add this line
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request.'}, status=400)



logger = logging.getLogger(__name__)

def generate_youtube_videos(request):
    """Handles YouTube video generation requests."""
    logger.info("generate_youtube_videos called")
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        prompt = request.POST.get('prompt', '')

        if prompt:
            try:
                api_key = next(_youtube_api_key_cycle)
                print(api_key)
                results = search_youtube(api_key, prompt) #search youtube function called
                if results:
                    logger.info(results)
                    return JsonResponse({'result': results})
                else:
                    return JsonResponse({'error': 'YouTube API request failed.'}, status=500)
            except Exception as e:
                logger.error(f"Error in generate_youtube_videos: {e}")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            logger.warning("Prompt is empty.")
            return JsonResponse({'error': 'Prompt is empty.'}, status=400)

    logger.warning("Invalid request to generate_youtube_videos.")
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def generate_quiz(request):
    """Generates a quiz using either the database or Gemini model with 50-50 chance."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        subtopic = json.loads(request.body).get('subtopic', '')
        topic = json.loads(request.body).get('topic', '')
        num_questions = int(json.loads(request.body).get('num_questions', 0))
        question_type = json.loads(request.body).get('question_type', '')

        if not all([topic, num_questions, question_type]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        try:
            # 50-50 chance to use database or Gemini
            use_database = random.choice([True, False])
            
            # Check available questions in database
            db_questions = QuizQuestion.objects.filter(
                topic__iexact=topic,
                question_type=question_type
            )
            
            if subtopic:
                db_questions = db_questions.filter(subtopic__iexact=subtopic)

            db_question_count = db_questions.count()
            
            if use_database and db_question_count >= num_questions:
                # Use database questions
                selected_questions = random.sample(list(db_questions), num_questions)
                quiz_data = {
                    "quiz": [
                        {
                            "id": q.id,
                            "type": q.question_type,
                            "question": q.question,
                            "options": q.options,
                            "correctAnswers": q.correct_answers,
                            "explanation": q.explanation
                        }
                        for q in selected_questions
                    ]
                }
                return JsonResponse({'quiz': quiz_data})
            
            # If we chose database but don't have enough questions, or chose Gemini
            # Get questions from Gemini
            prompt = f"""
                Create a quiz on the {'subtopic of ' + subtopic + ' within the broader topic of ' if subtopic else 'topic of '}{topic}. 
                The quiz should consist of {num_questions} questions. 
                All questions should be of type '{question_type}'.
                
                For each question, provide:
                    type: string;
                    question: string;
                    options: string[];
                    correctAnswers: number[];
                    explanation: string;
                
                Return the quiz in JSON format with a "quiz" key containing an array of questions.
            """
            
            response_text = call_gemini_model(prompt)
            quiz_data = eval(response_text)
            
            # Store new questions in database and collect their IDs
            final_questions = []
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
                            "correctAnswers": existing_question.correct_answers,
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
                            correct_answers=question["correctAnswers"],
                            explanation=question["explanation"],
                            source="gemini"
                        )
                        final_questions.append({
                            "id": new_question.id,
                            "type": new_question.question_type,
                            "question": new_question.question,
                            "options": new_question.options,
                            "correctAnswers": new_question.correct_answers,
                            "explanation": new_question.explanation
                        })
                except Exception as e:
                    logger.warning(f"Error processing question: {e}")
                    continue
            
            return JsonResponse({'quiz': {"quiz": final_questions}})

        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def test(request):
    return HttpResponse("Simple URL test: This is a test response.")