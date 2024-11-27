#!/bin/bash
export $(cat .env | xargs)

if [ ! -d ./.venv_recsys_bank ]; then
  echo "Виртуальное окружение не найдено. Создадим виртуальное окружение."
  pip install --upgrade pip
  python3 -m venv .venv_recsys_bank
  source ./.venv_recsys_bank/bin/activate
  echo "Установим зависимости"
  pip install -r requrements.txt
  screen screenmlflow server \
    --backend-store-uri postgresql://$DB_DESTINATION_USER:$DB_DESTINATION_PASSWORD@$DB_DESTINATION_HOST:$DB_DESTINATION_PORT/$DB_DESTINATION_NAME\
    --registry-store-uri postgresql://$DB_DESTINATION_USER:$DB_DESTINATION_PASSWORD@$DB_DESTINATION_HOST:$DB_DESTINATION_PORT/$DB_DESTINATION_NAME\
    --default-artifact-root s3://$S3_BUCKET_NAME\
    --no-serve-artifacts
  exit 1
fi

source ./.venv_recsys_bank/bin/activate
mlflow server \
  --backend-store-uri postgresql://$DB_DESTINATION_USER:$DB_DESTINATION_PASSWORD@$DB_DESTINATION_HOST:$DB_DESTINATION_PORT/$DB_DESTINATION_NAME\
  --registry-store-uri postgresql://$DB_DESTINATION_USER:$DB_DESTINATION_PASSWORD@$DB_DESTINATION_HOST:$DB_DESTINATION_PORT/$DB_DESTINATION_NAME\
  --default-artifact-root s3://$S3_BUCKET_NAME\
  --no-serve-artifacts