import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
USERS_FILE = "data/users.json"

client = Groq(api_key=GROQ_API_KEY)

user_histories = {}
user_topics = {}
active_tests = {}