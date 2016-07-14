import sys

if sys.platform[:3].lower() == 'win':
    aws_path = 'D:/temp/data/pdf/pdf_an/{dt}/'
else:
    aws_path = '/data/pdf/pdf_an/{dt}/'

# from aws s3 download pdf file to aws 84 server
SETTINGS = {
    'AWS_ACCESS_KEY_ID': 'AKIAOSAMH3FSTALUWXFA',
    'AWS_SECRET_ACCESS_KEY': '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',
    'AWS_HOST': 's3.cn-north-1.amazonaws.com.cn',
    'BUCKET_NAME': 'cn.com.chinascope.dfs',

    'MONGO_HOST': '122.144.134.95',
    'MONGO_PORT': 27017,
    'MONGO_DB': 'news',
    'MONGO_COLLECTION': 'announcement',

    'AWS_PATH': aws_path
}
