#!/bin/bash
# author: abner.R

# need root user to run 
cd /root/microscope
cd mysql
docker compose up -d
cd ../rabbitmq
docker compose up -d
cd ../redis
docker compoes up -d

# need common user to run 
cd /home/abenr/microscope/monitor
# pipenv shell 
pipenv run nohup celery -A monitor worker -l info >>/tmp/celery.log 2>&1 &
pipenv run nohup celery -A monitor beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler >> /tmp/celery_beat.log 2>&1 &
pipenv run nohup celery flower -A monitor --broker=amqp://rootcloud:celery@localhost:5672// >> /tmp/celery_flower.log 2>&1 &
pipenv run python manage.py runserver