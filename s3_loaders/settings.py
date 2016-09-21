import sys

if sys.platform[:3].lower() == 'win':
    aws_path = 'D:/temp/data/pdf/pdf_an/{dt}/'
else:
    aws_path = '/data/pdf/pdf_an/{dt}/'

# from aws s3 download pdf file to aws 84 server
SETTINGS = {
    'AWS_ACCESS_KEY_ID': '',
    'AWS_SECRET_ACCESS_KEY': '',
    'AWS_HOST': '',
    'BUCKET_NAME': '',

    'MONGO_HOST': '122.144.134.95',
    'MONGO_PORT': 27017,
    'MONGO_DB': 'news',
    'MONGO_COLLECTION': 'announcement',

    'AWS_PATH': aws_path
}
