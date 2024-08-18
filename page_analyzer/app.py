from flask import Flask
import os
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def hello():
    return "Hello, Project 3!"
