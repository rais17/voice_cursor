import os
from dotenv import load_dotenv
from openai import OpenAI
# from deepgram import DeepgramClient
from langchain_openai import ChatOpenAI
from pymongo import MongoClient

load_dotenv()

def require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Missing required env variable: {key}")
    return val

FFMPEG_PATH = "C:\\Users\\ARSHAD RAIS\\AppData\\Local\\Microsoft\\WinGet\\Links\\ffmpeg.exe"
MIC_DEVICE = "Microphone (High Definition Audio Device)"

openai_client = OpenAI(api_key=require_env("OPENAI_API_KEY"))
# deepgram_client = DeepgramClient(require_env("DEEPGRAM_API_KEY"))

chat_model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.5
)

mongo_client = MongoClient(os.getenv("MONGODB_URI"))