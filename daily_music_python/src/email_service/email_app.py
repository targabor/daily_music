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
    gunicorn_logger.info(html_path)
    body = ''
    gunicorn_logger.info(html_path)
    with codecs.open(html_path, 'r') as f:
        body = f.read()

    body = body.replace('#current_date', datetime.now().strftime('%Y-%m-%d'))
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['Subject'] = str(datetime.now().isocalendar().week) + '. Lit Letter'
    with open(image_path, 'rb') as f:
        img_data = f.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')
        msg.attach(image)

    gunicorn_logger.info(body)
    msg.attach(MIMEText(body, 'html'))
    mail_list = snowflake_functions.get_mail_list()
    gunicorn_logger.info(mail_list)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(from_email, app_password)
        for mail in mail_list:
            server.sendmail(from_email, mail, msg.as_string())
            gunicorn_logger.info(f'Email sent to {mail}')

    return make_response('Emails are sent', 200)


if __name__ == "__main__":
    app.run(debug=True)
