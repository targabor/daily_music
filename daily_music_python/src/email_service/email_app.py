import logging
import smtplib
import ssl
import os
import codecs

from flask import Flask, make_response
from src.snowflake_functions import snowflake_functions
from src.helpers import email_helper
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers

app_password = os.environ['APP_PASSWORD']
from_email = os.environ['FROM_EMAIL']
image_path = os.environ['IMAGE_PATH']


@app.route('/status', methods=['GET'])
def status():
    """Basic status check for email service status"""
    response = make_response('Email Service Status: OK', 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/send_mails_out', methods=['GET'])
def send_mails_out():
    """It sends the weekly newsletter for those who subscribed to it"""
    html_path = os.environ['HTML_PATH']
    mail_list = snowflake_functions.get_mail_list()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(from_email, app_password)
        for mail, id in mail_list:
            message = email_helper.generate_template_message(
                from_email, image_path, html_path, id)
            server.sendmail(from_email, mail, message.as_string())
            gunicorn_logger.info(f'Email sent to {mail}')

    return make_response('Emails are sent', 200)


@app.route('/leave_crew/<email_id>')
def leave_crew(email_id):
    """With this endpoint it is possible to leave the newsletter

    Args:
        email_id (str): the id of the email address
    """
    snowflake_functions.delete_email_address(email_id)
    return make_response('You are deleted from the mailing list. :( )', 200)


if __name__ == "__main__":
    app.run(debug=True)
