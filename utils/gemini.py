import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class Gemini():
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
    def get_response(self, query):
        return self.client.models.generate_content(
            model="gemini-2.0-flash", contents=str(query)
        ).text
