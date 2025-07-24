from dotenv import load_dotenv
import os

load_dotenv()

# Hata durumunda uyarı veren versiyon
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not found. Please check your .env file")