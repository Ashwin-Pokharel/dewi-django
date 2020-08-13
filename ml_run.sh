#!/bin/bash
docker pull apokhar/dewi

docker run -p "8501:8501" -p "8500:8500" -d  dewi-lms

if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo 'venv file is created'
else
  echo "venv exists!"
fi

sleep 1

source venv/bin/activate

pip3 install -r requirements.txt

python3 manage.py runserver
