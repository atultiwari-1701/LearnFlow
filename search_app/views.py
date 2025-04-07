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


# Configure logging (optional, for debugging)
logging.basicConfig(level=logging.DEBUG)

def call_gemini_model(prompt, model_name="gemini-2.0-pro-exp-02-05", temperature=1, top_p=0.95, top_k=64, max_output_tokens=8192, response_mime_type="application/json"):
    """
    Calls the Gemini model with the given prompt and configuration.
    """
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
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

Output a single valid JSON object inside the response with key as {topic}:

{
    "Short Description": {
        "Description": "Write a concise description between 100 and 120 words, using a friendly and conversational tone that encourages beginners. Highlight key points using **bold** text. **Example for 'Python':** **Python** is a versatile language known for its readability. It's used in web development, data science, and more." 
    },
    "Need to Learn {topic-name}": {
        "Description": "Explain in a maximum of 50 words why learning {topic-name} is valuable. Use a motivating, beginner-friendly tone. **Example for 'Python':** Learning Python opens doors to exciting career opportunities and empowers you to build innovative applications."
    },
    "Resource Tab Suggestions": {
        "Description": "Provide 3 resource tab name suggestions that would be most helpful for learning {topic-name}. Strictly select from the following options: 'Videos', 'Articles', 'Courses', 'Books', 'Documentation','Cheat Sheets','Practice Problems'. **Example for 'Python':** ['Videos', 'Documentations', 'Practice Problems']" 
    },
    "SubTopics": {
        "Description": {
            "subtopics": [
                {
                    "name": "Subtopic Name 1",
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
                    "name": "Subtopic Name 2",
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
                // Add more levels as needed (At least 3 levels are required)
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
        topic_name = request.POST.get('search_query', '')
        print(f"topic_name: {topic_name}")
        if topic_name:
            try:
                prompt = generate_prompt(topic_name)
                response_text = call_gemini_model(prompt)
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
                api_key = settings.YOUTUBE_API_KEY
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
    """Generates a quiz using the Gemini model."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        subtopic = request.POST.get('subtopic', '')
        topic = request.POST.get('topic', '')
        num_questions = request.POST.get('num_questions', '5')
        level = request.POST.get('level', 'beginner')
        question_type = request.POST.get('question_type', 'multiple-choice')

        if subtopic and topic:
            prompt = f"""
    Create a quiz on the subtopic of '{subtopic}' within the broader topic of '{topic}'. The quiz should consist of '{num_questions}' questions. The difficulty level of the questions should be '{level}'. All questions should be of type '{question_type}' (where Question Type is either 'multiple-choice' or 'true/false').

    For each question, provide:
    The question itself. The question should be clearly worded and unambiguous.

    If the question type is multiple-choice:
    Provide four answer options, labeled A, B, C, and D.
    Clearly indicate the correct answer(s). If there are multiple correct answers, provide them all.
    Indicate whether multiple answers are correct with a boolean flag: 'multiple_correct'. Set it to true if there are multiple correct answers, and false otherwise.

    If the question type is true/false:
    Clearly indicate the correct answer (True or False).

    The quiz should comprehensively test understanding of the core concepts and details within the specified subtopic. Ensure there are no duplicate questions and the answers are factually accurate. The subtopic should be narrow enough that {num_questions} questions at the specified level can be meaningfully generated. Prioritize clarity and conciseness in the questions and answers. The language must be appropriate for assessment. Avoid questions with subjective answers.

    Return the quiz in JSON format, with the following structure: `[{{\"question\": \"Question text\", \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"], \"answer\": [\"Correct Answer 1\", \"Correct Answer 2\", ...], \"multiple_correct\": true/false}}]` for multiple choice, and `[{{\"question\": \"Question text\", \"answer\": \"True/False\"}}]` for true/false questions. If the subtopic is too broad or narrow to generate the requested number of questions, return an error message in json format: `{{\"error\": \"error message\"}}`
                """

            try:
                response_text = call_gemini_model(prompt)  # Use your function
                quiz_data = eval(response_text) #evaluate the response text to a python object.
                logger.info('Generated Quiz Response: %s', quiz_data)
                return JsonResponse({'quiz': quiz_data})
            except Exception as e:
                logger.error(f"Error generating quiz: {e}")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Subtopic or topic is empty.'}, status=400)
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def test(request):
    return HttpResponse("Simple URL test: This is a test response.")