import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape

from scanning import Notification

APP_SECRET_PASSWORD = "yiml qbir yjiy orsq"

TEMP_NAME = "Amir" #TODO

def create_message(notification, sender_email, receiver_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = notification.type
    message["From"] = sender_email
    message["To"] = receiver_email

    html = environment.get_template("email_notification.html").render(notification=notification, name=TEMP_NAME)
    message.attach(MIMEText(html, "html"))

    # Open the logo image in binary mode
    with open('static/favicon.ico', 'rb') as img_file:
        img_data = img_file.read()

    # Create the image part
    img_part = MIMEImage(img_data, 'image/ico')
    img_part.add_header('Content-ID', '<logo_image>')  # Set content ID for reference in HTML
    message.attach(img_part)

    return message

def send_email(sender_email, receiver_email, message):
    port = 465  # For SSL

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("romthebarbarian@gmail.com", APP_SECRET_PASSWORD)
        server.sendmail(sender_email, receiver_email, message.as_string())

def send_email_notification(notification : Notification, sender_email:str, receiver_email : str):
    message = create_message(notification, sender_email,receiver_email)
    send_email(sender_email, receiver_email, message)
    print(message)

# def send_notification(notification):
#     global environment
#     environment = Environment(loader=FileSystemLoader("templates/"))

if __name__ == '__main__':
    global environment
    environment = Environment(autoescape=select_autoescape(['html', 'xml']),loader=FileSystemLoader("templates/"))
    send_email_notification(Notification("DOS Attack", "Network Problems", "Possible DOS attack from '192.168.1.52'"),"neteye@gmail.com","savvasapir@gmail.com")