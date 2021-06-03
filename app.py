import os
import secrets

import flask_restful as restful

from flask import Flask, render_template
from waitress import serve


def create_app():
    # Create images directory
    os.makedirs(os.path.join('static', 'images'), exist_ok=True)

    # Setup flask app
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', secrets.token_urlsafe())
    # Max of 5MB for files
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    # Allowed ext
    app.config['UPLOAD_EXTENSIONS'] = ['.txt']
    # Uploads folder
    os.makedirs('uploads', exist_ok=True)
    app.config['UPLOAD_PATH'] = 'uploads'

    # Blueprints & Routes
    from main.routes.part_of_speech import pos
    from main.routes.subtree_metric import stm
    from main.routes.sentence_trees import sentence_trees
    from main.routes.n_gram_metrics import n_gram_metrics
    app.register_blueprint(n_gram_metrics.bp)
    app.register_blueprint(sentence_trees.bp)
    app.register_blueprint(stm.bp)
    app.register_blueprint(pos.bp)

    # REST API
    from main.routes.part_of_speech.processing import POSAPI
    from main.routes.sentence_trees.processing import SentenceTreesAPI
    api = restful.Api(app)
    api.add_resource(POSAPI, '/api/pos')
    api.add_resource(SentenceTreesAPI, '/api/sentence-trees')

    return app


APP = create_app()


@APP.route('/')
def home_page():
    return render_template('home.html', title='Home Page')


if __name__ == '__main__':
    serve(APP, host='0.0.0.0', port=5000)
