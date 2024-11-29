import boto3
from dotenv import load_dotenv
import os
import logging

load_dotenv()

class Config:
    """
    Класс для хранения конфигурационных переменных для работы с AWS S3.
    """
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_SERVICE_NAME = 's3'
    S3_ENDPOINT_URL = 'https://storage.yandexcloud.net'


def get_session():
    """
    Функция для создания сессии для работы с AWS S3.
    """

    session = boto3.session.Session()

    return session.client(
        service_name=Config.S3_SERVICE_NAME,
        endpoint_url=Config.S3_ENDPOINT_URL,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
    )

def list_objects(bucket_name):
    """
    Функция для вывода списка объектов в указанном ведре AWS S3.

    Аргументы:
    - bucket_name: имя ведра AWS S3.

    Возвращает список ключей объектов в ведре.
    """

    s3 = get_session()

    try:
        if s3.list_objects(Bucket=bucket_name).get('Contents'):
            for key in s3.list_objects(Bucket=bucket_name)['Contents']:
                print(key['Key'])
    except Exception as e:
        logging.error(f"Ошибка при выполнении операции: {e}")


if __name__ == '__main__':
    bucket_name = 's3-student-mle-20240325-d5eb3b4dad'
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    try:
        list_objects(bucket_name)
    except Exception as e:
        logger.error(f"Ошибка при выполнении программы: {e}")

    list_objects(bucket_name)
