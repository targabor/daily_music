import slack
import os
import logging
import json

from flask import Flask, make_response, request

app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers


@app.route('/status', methods=['GET'])
def status():
    """Basic status check for spotify_app status"""
    response = make_response('Spotify App Status: OK', 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


if __name__ == "__main__":
    app.run(debug=True)
