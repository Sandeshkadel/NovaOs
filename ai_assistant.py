import requests
import os
from datetime import datetime

GEMINI_API_KEY = "AIzaSyAd09_-8"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

def ask_gemini(prompt, context=None):
    headers = {"Content-Type": "application/json"}
    
    # Build the prompt with context
    full_prompt = prompt
    if context:
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
    
    body = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 50,
            "topP": 0.95,
            "maxOutputTokens": 1024
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }
    
    try:
        response = requests.post(GEMINI_API_URL, json=body, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Sorry, I couldn't generate a response. Please try again."
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm having trouble connecting to the AI service. Please try again later."
    except Exception as e:
        print(f"Error processing Gemini response: {e}")
        return "An error occurred while processing your request."

def log_interaction(prompt, response, username):
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - User: {username}\nPrompt: {prompt}\nResponse: {response}\n\n"
    
    try:
        with open("ai_interactions.log", "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error logging interaction: {e}")