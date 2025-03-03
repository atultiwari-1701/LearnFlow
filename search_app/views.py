import os
import json
import traceback
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from google import genai
from google.genai import types
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

Output a single valid JSON object containing:

{
    "Short Description": {
        "Description": "Write a concise description between 70 and 100 words, using a friendly and conversational tone that encourages beginners. Highlight key points using **bold** text. **Example for 'Python':** **Python** is a versatile language known for its readability. It's used in web development, data science, and more." 
    },
    "Need to Learn {topic-name}": {
        "Description": "Explain in a maximum of 50 words why learning {topic-name} is valuable. Use a motivating, beginner-friendly tone. **Example for 'Python':** Learning Python opens doors to exciting career opportunities and empowers you to build innovative applications."
    },
    "SubTopics of {topic-name}": {
        "Description": {
            "subtopics": [
                {
                    "name": "Subtopic Name 1",
                    "description": "20-30 word description. **Example for 'Python Variables':** Understanding how to store and manipulate data.",
                    "difficulty": "Beginner, Intermediate, Advanced, Expert, Mastery. **Example for 'Python Variables':** Beginner",
                    "timeToComplete": "e.g., 2 hours. **Example for 'Python Variables':** 2 hours",
                    "whyItMatters": "20-30 word explanation. **Example for 'Python Variables':** Fundamental for all Python programming tasks.",
                    "commonMistakes": [
                        "**Example for 'Python Variables':** Using incorrect data types.",
                        "**Example for 'Python Variables':** Not understanding variable scope.",
                        "**Example for 'Python Variables':** Naming variables poorly."
                    ],
                    "resourceTabs": [
                        'resourceTabs' JSON array object containing three resource tab names (e.g., 'Articles', 'Videos', 'News', 'Interactive','Courses') to indicate the types of resources available for this subtopic. Do not include website links or descriptions.
                    ]
                },
                {
                    "name": "Subtopic Name 2",
                    "description": "20-30 word description. **Example for 'Python Loops':** Learning to control program flow.",
                    "difficulty": "Beginner, Intermediate, Advanced, Expert, Mastery. **Example for 'Python Loops':** Intermediate",
                    "timeToComplete": "e.g., 2 hours. **Example for 'Python Loops':** 3 hours",
                    "whyItMatters": "20-30 word explanation. **Example for 'Python Loops':** Enables you to write efficient code.",
                    "commonMistakes": [
                        "**Example for 'Python Loops':** Incorrect loop conditions.",
                        "**Example for 'Python Loops':** Not handling edge cases.",
                        "**Example for 'Python Loops':** Using infinite loops."
                    ],
                    "resourceTabs": [
                        'resourceTabs' JSON array object containing three resource tab names (e.g., 'Articles', 'Videos', 'News', 'Interactive','Courses') to indicate the types of resources available for this subtopic. Do not include website links or descriptions.
                    ]
                },
                // Add more subtopics as needed
            ]
        }
    },
    "Road Map to Learn {topic-name}": {
        "Description": {
            "prerequisites": {
                "description": "Prerequisite information. **Example for 'Python':** Basic computer literacy."
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
                // Add more levels as needed
            ]
        }
    },
    "Resource Tab Suggestions for {topic-name}": {
        "Description": "Provide 3 resource tab name suggestions that would be most helpful for learning {topic-name}. **Example for 'Python':** ['Tutorials', 'Videos', 'Documentation']"
    },
    "Key Takeaways": {
        "Description": "A JSON array containing 3-5 concise, impactful takeaways that summarize the most important points of learning {topic-name}. Each takeaway should be a short, direct statement. **Example for 'Python':** ['Python is versatile and beginner-friendly.', 'Practice is essential to mastering Python.', 'Python has a rich ecosystem of libraries.', 'Python is used in web development, data science, and automation.', 'Python promotes code readability and maintainability.']"
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
            // Add more FAQs as needed
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
            // Add more related topics as needed
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

def test(request):
    return HttpResponse("Simple URL test: This is a test response.")