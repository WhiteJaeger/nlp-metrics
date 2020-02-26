import secrets
from flask import Flask
from os import path, getenv
from joblib import load
import pathlib


def create_app():
    # Load pre-trained model
    project_path = str(pathlib.Path(__file__).parents[1])
    model_path = path.join(project_path, 'models', 'crfWJSModel90k.joblib')
    crf = load(model_path)

    # Setup flask app
    app = Flask(__name__)
    app.secret_key = getenv('SECRET_KEY', secrets.token_urlsafe())

    return app, crf


APP, CRF_MODEL = create_app()
