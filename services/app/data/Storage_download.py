import boto3
from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_SERVICE_NAME = 's3'
    S3_ENDPOINT_URL = 'https://storage.yandexcloud.net'


def get_session():
    session = boto3.session.Session()

    return session.client(
        service_name=Config.S3_SERVICE_NAME,
        endpoint_url=Config.S3_ENDPOINT_URL,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
    )

if __name__ == '__main__':
    bucket_name = 's3-student-mle-20240325-d5eb3b4dad'
    s3 = get_session()
    file_names = ['top_popular.parquet', 'similar.parquet', 'recommendations_u.parquet']
    file_name_s3_path = 'recsys/recommendations/'

    for file_name in file_names:
        s3.download_file(Bucket=bucket_name, Key=file_name_s3_path + file_name, Filename=file_name)
        print(f'{file_name} успешно выгружен из {bucket_name} под именем {file_name}.')
        print(' ')

    print('Все файлы успешно выгружены.')
