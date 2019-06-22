import json
import smtplib
import os

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.cloud import vision
from google.cloud import storage


def handler(event, context):

   print(json.dumps(event, indent=3))

   send_grid_api_key = os.environ.get('SEND_GRID_API_KEY', None)
   send_grid_domain = os.environ.get('SEND_GRID_DOMAIN', None)

   bucket = event['bucket']
   object_key = event['name']
   image_uri = 'gs://' + bucket + '/' + object_key

   object_attr = object_key.split('/')
   user_email = object_attr[0]
   camera_name = object_attr[1]
   phone_location = object_attr[2]
   
   if phone_location == "away":
      client = vision.ImageAnnotatorClient()
      response = client.face_detection({'source': {'image_uri': image_uri}})
      faces = response.face_annotations   
      print("Number of faces found: " + str(len(faces)))
      if len(faces) > 0:
         subject = "MOTION DETECTED AND FACE RECOGNISED"
         from_addr = bucket + "@" + send_grid_domain
         client = storage.Client()
         bucket = client.get_bucket(bucket)
         blob = bucket.get_blob(object_key)
         attachment = blob.download_as_string()
         msg = MIMEMultipart()
         msg['Subject'] = subject
         msg['From'] = from_addr
         msg['To'] = user_email
         part = MIMEText("Motion has been detected on " + camera_name + ":")
         msg.attach(part)
         part = MIMEApplication(attachment)
         part.add_header('Content-Disposition', 'attachment', filename = "image.jpg")
         part.add_header('Content-Type', 'image/jpeg; charset=UTF-8')
         msg.attach(part)
         try:
            server = smtplib.SMTP_SSL('smtp.sendgrid.net', 465)
            server.ehlo()
            server.login('apikey', send_grid_api_key)
            server.sendmail(from_addr, user_email, msg.as_string())
            server.close()
            print("Email notification sent")
         except:
            print("Error sending email")
      else:
         print("Motion detected but no face recognised")
   else:
      print("Motion detected, but phone located at home so facial recognition not performed")
