# [START app]
import logging

# Imports the Google Cloud client library
# from google.cloud import storage

# Imports speech analysis code
import speech_analysis

# [START imports]
from flask import Flask, render_template, request
import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
# [END imports]

# [START create_app]
app = Flask(__name__)
# [END create_app]


# [START form]
@app.route('/form')
def form():
    return render_template('form.html')
# [END form]


# [START submitted]
@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    email = request.form['email']
    comments = request.form['comments']

    # TODO: fix so saving files works
    if request.method == 'POST':
        print('I got in')
        files = request.files['audio']
        files.save(secure_filename(files.filename))

    # Call speech analysis with audio filename to get json insights
    # insights = speech_analysis.speechanalysis(audio_filename)

    # Instantiates a client
    #storage_client = storage.Client()

    # [END submitted]
    # [START render_template]
    return render_template(
        'submitted_form.html',
        name=name,
        email=email,
        comments=comments)
    # [END render_template]


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
