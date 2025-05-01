import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') #or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') #or 'mysql+mysqlconnector://root:682022@localhost/gym_management'
    SQLALCHEMY_TRACK_MODIFICATIONS = False