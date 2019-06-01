import base64
import json
from os import environ
from google.cloud import bigquery

def handler(event, context):

   print("Event:")
   print(json.dumps(event, indent=3))
   data = base64.b64decode(event['data'])
   print("Data:")
   print(data)

   dataset_id = environ.get('BIGQUERY_DATASET_ID', None)
   print(dataset_id)
   table_id = environ.get('BIGQUERY_TABLE_ID', None)
   print(table_id)

   client = bigquery.Client()
   table_ref = client.dataset(dataset_id).table(table_id)
   table = client.get_table(table_ref)

   errors = client.insert_rows_json(table, data)
   assert errors == []
