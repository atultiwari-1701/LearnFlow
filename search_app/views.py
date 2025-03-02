# search_app/views.py
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
                "Description": "A JSON object containing subtopics for learning {topic-name} as 'Key' with a 20-30 word description as the 'value'. Include a 'Difficulty' rating ('Beginner', 'Intermediate', 'Advanced', 'Expert', 'Mastery'), an estimated 'Time to Complete' (e.g., '2 hours'), a 'Why it Matters' explanation (20-30 words), a 'Common Mistakes' JSON object that contains 3 specific mistakes relevant to the subtopic's difficulty level and how to avoid them, and a 'Resource Tabs' JSON object containing three resource tab names (e.g., 'Articles', 'Videos', 'News', 'Interactive') to indicate the types of resources available for this subtopic. Do not include website links or descriptions."
            },
            "Road Map to Learn {topic-name}": {
                "Description": "A JSON object detailing prerequisites for learning {topic-name}, followed by a structured learning roadmap from basic to advanced levels. Each level should include: a 'Topics' JSON object with sub-divisions and clear directions, a 'How to Conquer' section with actionable advice, and 'Insider Tips' in a maximum of 50 words."
            },
            "Resource Tab Suggestions for {topic-name}":{
                "Description": "Provide 3 resource tab name suggestions that would be most helpful for learning {topic-name}. Example : 'Articles','Videos','Tutorials', 'Courses'."
            },
            "Key Takeaways": {
                "Description": "A JSON object containing 3-5 key takeaways that summarize the most important points of learning {topic-name}."
            },
            "Frequently Asked Questions": {
                "Description": "A JSON object containing 3-5 frequently asked questions about {topic-name} with concise answers."
            },
            "Related Topics": {
                "Description": "A JSON object containing 3-5 related topics to {topic-name} with brief descriptions."
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
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                model = "gemini-2.0-pro-exp-02-05"
                prompt = generate_prompt(topic_name)
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(
                                text=prompt
                            ),
                        ],
                    ),
                ]
                generate_content_config = types.GenerateContentConfig(
                    temperature=1,
                    top_p=0.95,
                    top_k=64,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                )

                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                )

                print("Gemini API call successful")
                return JsonResponse({'result': response.text})

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