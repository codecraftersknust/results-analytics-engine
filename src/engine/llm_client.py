import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY environment variable not set. AI features will not work.")

def get_gemini_model(model_name="gemini-2.5-flash"):
    """
    Returns a configured Gemini GenerativeModel instance.
    For extraction tasks, gemini-1.5-pro is recommended for its large context window and strong instruction following.
    For fast NLP tasks, gemini-1.5-flash can be used.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set. Please set it in your .env file.")
    
    return genai.GenerativeModel(model_name)
