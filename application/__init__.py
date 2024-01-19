"""
This file is the main file of the application. It contains the configuration of the application.
"""

import json
from flask import Flask
from pymongo import MongoClient
import boto3


def read_credentials(filename):
    """
    Read credentials from a file
    """
    with open(filename) as json_file:
        creds = json.load(json_file)
    return creds


creds = read_credentials('credentials.json')

my_bucket_name = creds['bucket_name']
my_bucket_region = creds['bucket_region']

app = Flask(__name__)
# app.secret_key= my_app_secret_key
app.secret_key = creds
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

try:
    client = MongoClient(creds['mongo_uri'])

    db_mongo_company = client.get_database(creds['company_collection'])
    db_mongo_job = client.get_database(creds['job_application_collection'])
    db_mongo_food = client.get_database(creds['food_data_collection'])
    db_mongo_keywords = client.get_database(creds['keywords_collection'])
    db_mongo_weight = client.get_database(creds['weight_collection'])

    s3 = boto3.resource(creds['amazon_service'],
                        aws_access_key_id= creds['aws_access_key_id'],
                        aws_secret_access_key= creds['aws_secret_access_key'])

    bucket = s3.Bucket(my_bucket_name)
except Exception as e:
    print(e)

from application import routes
