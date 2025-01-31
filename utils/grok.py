import os
from dotenv import load_dotenv
from openai import OpenAI

class Grok():
    def __init__(self):     
        load_dotenv()   
        XAI_API_KEY = os.getenv("XAI_API_KEY")
        self.client = OpenAI(
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1",
        )
        
    def chat(self, message):
        completion = self.client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "user", "content": message}                
            ],
        )

        response = completion.choices[0].message.content
        return response