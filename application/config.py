import os
from urllib.parse import quote

SECRET_KEY = os.environ.get('SECRET_KEY')
PORT = 5080

HOST=os.environ.get('HOST')
POSTGRE_PORT=os.environ.get('PORT')
USER=os.environ.get('USER')
PASS=quote(os.environ.get('PASSWORD'))
DATABASE=os.environ.get('DATABASE')

SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{USER}:{PASS}@{HOST}:{POSTGRE_PORT}/{DATABASE}'
SQLALCHEMY_TRACK_MODIFICATIONS = False