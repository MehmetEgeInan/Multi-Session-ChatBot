from database import Database
import uuid
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
db = Database()

class ChatBot:
    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        if not session_id:
            db.create_session(self.session_id)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def chat(self, user_input):
        db.save_message(self.session_id, 'user', user_input)
        response = self._get_ai_response(user_input)
        db.save_message(self.session_id, 'assistant', response)
        return response
    
    def _get_ai_response(self, user_input):
        try:
            history = db.get_messages(self.session_id)
            messages = [{"role": "system", "content": "Kısa ve net cevaplar ver."}]
            
            for role, content, _ in history[-5:]:
                messages.append({"role": role, "content": content})
            
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Hata: {str(e)}"
    
    def get_history(self):
        return db.get_messages(self.session_id)
    
    @staticmethod
    def get_all_sessions():
        return db.get_all_sessions()
    
    @staticmethod
    def delete_session(session_id):
        db.delete_session(session_id)
    
    @staticmethod
    def create_new_session():
        new_id = str(uuid.uuid4())
        db.create_session(new_id)
        return new_id