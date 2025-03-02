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
        "Description": "Write a concise description between 70 and 100 words, using a friendly and conversational tone that encourages beginners. Highlight key points using **bold** text."
    },
    "Need to Learn {topic-name}": {
        "Description": "Explain in a maximum of 50 words why learning {topic-name} is valuable. Use a motivating, beginner-friendly tone."
    },
    "SubTopics of {topic-name}": {
        "Description": {
            "subtopics": [
                {
                    "name": "Subtopic Name 1",
                    "description": "20-30 word description.",
                    "difficulty": "Beginner, Intermediate, Advanced, Expert, Mastery",
                    "timeToComplete": "e.g., 2 hours",
                    "whyItMatters": "20-30 word explanation.",
                    "commonMistakes": [
                        "Mistake 1",
                        "Mistake 2",
                        "Mistake 3"
                    ],
                    "resourceTabs": [
                        "Articles", "Videos", "News", "Interactive"
                    ]
                },
                {
                    "name": "Subtopic Name 2",
                    "description": "20-30 word description.",
                    "difficulty": "Beginner, Intermediate, Advanced, Expert, Mastery",
                    "timeToComplete": "e.g., 2 hours",
                    "whyItMatters": "20-30 word explanation.",
                    "commonMistakes": [
                        "Mistake 1",
                        "Mistake 2",
                        "Mistake 3"
                    ],
                    "resourceTabs": [
                        "Articles", "Videos", "News", "Interactive"
                    ]
                },
                // Add more subtopics as needed
            ]
        }
    },
    "Road Map to Learn {topic-name}": {
        "Description": {
            "prerequisites": {
                "description": "Prerequisite information."
            },
            "levels": [
                {
                    "name": "Basic Level",
                    "topics": [
                        "Topic 1",
                        "Topic 2",
                        "Topic 3"
                    ],
                    "howToConquer": "Actionable advice.",
                    "insiderTips": "50-word tips."
                },
                {
                    "name": "Intermediate Level",
                    "topics": [
                        "Topic 1",
                        "Topic 2",
                        "Topic 3"
                    ],
                    "howToConquer": "Actionable advice.",
                    "insiderTips": "50-word tips."
                },
                // Add more levels as needed
            ]
        }
    },
    "Resource Tab Suggestions for {topic-name}": {
        "Description": ["Articles", "Videos", "Tutorials", "Courses"]
    },
    "Key Takeaways": {
        "Description": [
            "Takeaway 1",
            "Takeaway 2",
            "Takeaway 3",
            "Takeaway 4",
            "Takeaway 5"
        ]
    },
    "Frequently Asked Questions": {
        "Description": [
            {
                "question": "Question 1",
                "answer": "Answer 1"
            },
            {
                "question": "Question 2",
                "answer": "Answer 2"
            },
            // Add more FAQs as needed
        ]
    },
    "Related Topics": {
        "Description": [
            {
                "topic": "Topic 1",
                "description": "Description 1"
            },
            {
                "topic": "Topic 2",
                "description": "Description 2"
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