"""
This file is the main file of the application. It contains the configuration of the application.
"""

import json
from flask import Flask
from pymongo import MongoClient
import boto3
from .llmKW import KeyWordExtractor, PDFExtractor
import torch
import psycopg2

device = "cuda" if torch.cuda.is_available() else "cpu"
extractor = KeyWordExtractor(device=device, num_workers=4)
pdf_extractor = PDFExtractor(device=device, num_workers=4)

def read_credentials(filename):
    with open(filename) as json_file:
        creds = json.load(json_file)
    return creds

creds = read_credentials('credentials.json')

DB_HOST = creds['host']
DB_NAME = creds['database']
DB_USER = creds['user']
DB_PASS = creds['password']
DB_PORT = creds['port']

con = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

if con:
    print("Connected Successfully")

my_bucket_name = creds['bucket_name']
my_bucket_region = creds['bucket_region']

app = Flask(__name__)
app.secret_key = creds['app_secret_key']
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
