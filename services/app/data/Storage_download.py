import boto3
from dotenv import load_dotenv
import os
import logging

load_dotenv()

class Config:
    """
    Класс для хранения конфигурационных параметров для работы с AWS S3.

    Свойства:
    - AWS_ACCESS_KEY_ID: Идентификатор доступа AWS.
    - AWS_SECRET_ACCESS_KEY: Секретный ключ доступа AWS.
    - S3_SERVICE_NAME: Имя сервиса AWS S3.
    - S3_ENDPOINT_URL: URL конечной точки AWS S3.
    """
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_SERVICE_NAME = 's3'
    S3_ENDPOINT_URL = 'https://storage.yandexcloud.net'


def get_session():
    """
    Возвращает:
    - session: Сессия для работы с AWS S3.
    """
    session = boto3.session.Session()

    return session.client(
        service_name=Config.S3_SERVICE_NAME,
        endpoint_url=Config.S3_ENDPOINT_URL,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
    )

def download_files(bucket_name, file_names, file_name_s3_path):
    """
    Функция для загрузки файлов из AWS S3.

    Параметры:
    - bucket_name: Имя бакета AWS S3.
    - file_names: Список имен файлов для загрузки.
    - file_name_s3_path: Путь к файлам в бакете AWS S3.
    """
    s3 = get_session()

    for file_name in file_names:
        try:
            s3.download_file(Bucket=bucket_name, Key=file_name_s3_path + file_name, Filename=file_name)
            logging.info(f'{file_name} успешно выгружен из {bucket_name} под именем {file_name}.')
        except Exception as e:
            logging.error(f'Ошибка при загрузке файла {file_name}: {e}')

if __name__ == '__main__':
    bucket_name = 's3-student-mle-20240325-d5eb3b4dad'
    file_names = ['top_popular.parquet', 'similar.parquet', 'recommendations_u.parquet']
    file_name_s3_path = 'recsys/recommendations/'
    try:        
        logging.basicConfig(level=logging.INFO)
        download_files(bucket_name, file_names, file_name_s3_path)
    except Exception as e:
        logging.error(f'Ошибка при загрузке файла {file_name}: {e}')
