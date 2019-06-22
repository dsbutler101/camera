#!/usr/bin/env python3

import os, sys, socket, re
from os.path import isfile, basename

from google.cloud import storage
from google.cloud import pubsub


BUCKET_NAME = os.environ['BUCKET_NAME']
IMAGE_PATH = "/home/pi/Documents/motion/"
USERNAME = os.environ['USERNAME']
SERVICE_NAME = os.environ['SERVICE_NAME']
LOCK_FILE = os.path.expanduser("~") + "/IPHONE-AT-HOME"


def upload_image(params):
   image_files = os.listdir(IMAGE_PATH)
   image_files.sort(
      reverse = True,
      key = lambda str: re.sub("^[0-9]*-", "", str)
   )
   for image_file in image_files[100:]:
      print("Deleting old image file not uploaded: " + image_file)
      try:
         os.remove(IMAGE_PATH + image_file)
      except Exception as e:
         print("Error deleting image file: " + image_file + " error: " + str(e))
   image = params[0]
   
   #cw = boto3.client('cloudwatch')
   print("Uploading image to Google Cloud Storage: " + image)
   try:
      if isfile(LOCK_FILE):
         location = "home"
      else:
         location = "away"
      storage_client = storage.Client.from_service_account_json('/home/pi/key-file.json')
      bucket = storage_client.bucket(BUCKET_NAME)
      name =  USERNAME + "/" + SERVICE_NAME + "/" + location + "/" + basename(image)
      blob = storage.blob.Blob(name, bucket)
      blob.upload_from_filename(image)
      os.remove(image)
      print("Image uploaded successfully.")
   except Exception as e:
      print("Error uploading image to Google Cloud Storage: " + str(e))


if __name__ == '__main__':
   upload_image(sys.argv[1:])
