import json
from flask import Flask
from pymongo import MongoClient
import boto3

# read aws credentials from file
with open('credentials.json') as json_file:
    data = json.load(json_file)
    my_aws_access_key_id = data['aws_access_key_id']
    my_aws_secret_access_key = data['aws_secret_access_key']

    my_app_secret_key = data['app_secret_key']

    my_mongo_uri = data['mongo_uri']

    my_bucket_name = data['bucket_name']
    my_bucket_region = data['bucket_region']

    my_food_data_collection = data['food_data_collection']
    my_job_application_collection = data['job_application_collection']
    
    my_amazon_service = data['amazon_service']

app = Flask(__name__)
app.secret_key= my_app_secret_key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

try:
    client = MongoClient(my_mongo_uri)

    db_mongo_job = client.get_database(my_job_application_collection)
    db_mongo_food = client.get_database(my_food_data_collection)

    s3 = boto3.resource(my_amazon_service, 
                        aws_access_key_id= my_aws_access_key_id,
                        aws_secret_access_key= my_aws_secret_access_key
                        )

    bucket = s3.Bucket(my_bucket_name)
except Exception as e:
    print(e)

from application import routes
