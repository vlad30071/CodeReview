#!/bin/bash

docker-compose down
docker-compose up --build -d
docker-compose exec web flask
docker-compose ps