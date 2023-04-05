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

    pass
