from dotenv import load_dotenv
import os

load_dotenv()
BACKEND_URL = os.getenv('BACKEND_URL')
FRONTEND_URL = os.getenv('FRONTEND_URL')
POSTGRES_URL = os.getenv('POSTGRES_URL')
TOKEN = os.getenv('TOKEN')