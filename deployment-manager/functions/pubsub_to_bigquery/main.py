#!/usr/bin/env python3

import base64
import json
import smtplib
from os import environ
from datetime import datetime
from google.cloud import bigquery
from google.cloud import vision
from google.cloud import storage

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SEND_GRID_API_KEY = environ.get('SEND_GRID_API_KEY', None)
SEND_GRID_DOMAIN = environ.get('SEND_GRID_DOMAIN', None)
# do we need this environment variable as we can also get this from pubsub message
BUCKET_NAME = environ.get('BUCKET_NAME')

def handler(event, context):

   data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
   print(data)
   for i, d in enumerate(data):
      data[i]['receive_time'] = str(datetime.utcnow())
      if not d['phone_at_home'] and 'file_object' in d:
         user_email = d['user_email']
         camera_name = d['camera_name']
         url = d['file_object'].replace('gs://', '')
         bucket_name, path = url.split('/', 1)
         client = vision.ImageAnnotatorClient()
         response = client.face_detection({'source': {'image_uri': d['file_object']}})
         faces = response.face_annotations
         data[i]['num_faces'] = len(faces)
         print("Number of faces found: " + str(len(faces)))
         if len(faces) > 0:
            subject = "MOTION DETECTED AND FACE RECOGNISED"
            from_addr = BUCKET_NAME + "@" + SEND_GRID_DOMAIN
            client = storage.Client()
            bucket = client.get_bucket(BUCKET_NAME)
            blob = bucket.get_blob(path)
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
               server.login('apikey', SEND_GRID_API_KEY)
               server.sendmail(from_addr, user_email, msg.as_string())
               server.close()
               print("Email notification sent")
            except:
               print("Error sending email")
         else:
            print("Motion detected but no face recognised")
      else:
         print("Phone at home or no image uploaded so facial recognition not performed")


   dataset_id = environ.get('BIGQUERY_DATASET_ID', None)
   table_id = environ.get('BIGQUERY_TABLE_ID', None)
   client = bigquery.Client()

   table_ref = client.dataset(dataset_id).table(table_id)
   table = client.get_table(table_ref)
   errors = client.insert_rows_json(table, data)
   assert errors == []
