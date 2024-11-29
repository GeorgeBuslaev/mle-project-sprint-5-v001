#!/bin/bash

if [ ! -d ./.venv_recsys_bank ]; then
  echo "Виртуальное окружение не найдено. Создадим виртуальное окружение."
  pip install --upgrade pip
  python3 -m venv .venv_recsys_bank
  source ./.venv_recsys_bank/bin/activate
  echo "Установим Jupyter Lab и создадим Kernel"
  pip install -r requirements.txt
  python -m ipykernel install --user --name=mle-bank-recsys-kernel
  jupyter lab --no-browser
  exit 1
fi

source ./.venv_recsys_bank/bin/activate
jupyter lab --no-browser
