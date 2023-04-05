import codecs

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def generate_template_message(from_email: str, image_path: str, html_path: str, gunicorn_logger):
    """It generates the template message for the newsletter

    Args:
        from_email (str): email address of the sender
        image_path (str): path of the image in the html
        html_path (str): path of the html message

    Returns:
        _type_: _description_
    """
    body = ''
    gunicorn_logger.info(html_path)
    with codecs.open(html_path, 'r') as f:
        body = f.read()

    gunicorn_logger.info(body)
    body.replace('#current_date', datetime.now().strftime('%Y-%m-%d'))
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['Subject'] = str(datetime.now().isocalendar().week) + '. Lit Letter'
    with open(image_path, 'rb') as f:
        img_data = f.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')
        msg.attach(image)

    msg.attach(MIMEText(body, 'html'))

    return msg
