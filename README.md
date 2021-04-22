# NLP Metrics
## N-gram based and Syntactic

This repository contains Flask web application which aims to help with measuring the performance of machine & human translation. This app could be accessed either remotely - it is deployed at http://nlp-metrics.herokuapp.com/ - or locally - by following these steps.

## Running app locally

* Prerequisites:

    * Python version >= 3.7.

    * It is strongly advised to create a [virtual environment](https://docs.python.org/3/library/venv.html) for the app.

1. Install dependencies by running the following command:

    ```bash
    pip install -r requirements.txt
    ```
2. Download the following corpora: stopwords with NLTK downloader:
    ```bash
    python -m nltk.downloader stopwords
    ```
3. Run the application:
    1. In production mode: `python app.py`
    2. In development mode:
        1. Set env variables: `set or export FLASK_APP=app.py`
        2. Run the app: `flask run`
4. Head to the `localhost:5000` in browser.
