import logging
import smtplib
import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, make_response, request
from src.snowflake_functions import snowflake_functions

app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers


@app.route('/status', methods=['GET'])
def status():
    """Basic status check for email service status"""
    response = make_response('Email Service Status: OK', 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/send_mails_out', methods=['GET'])
def send_mails_out():
    gunicorn_logger.warning(dir(snowflake_functions))
    mail_list = snowflake_functions.get_mail_list()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login('daily.music.letter@gmail.com', 'nluubjspujndruou')
        for mail in mail_list:
            msg = MIMEMultipart()
            msg['From'] = 'daily.music.letter@gmail.com'
            msg['To'] = mail
            msg['Subject'] = 'Test email from Python'
            body = 'This is a test email sent from Python.'
            msg.attach(MIMEText(body, 'plain'))
            server.sendmail('daily.music.letter@gmail.com',
                            mail, msg.as_string())
    return make_response('OK', 200)


if __name__ == "__main__":
    app.run(debug=True)
