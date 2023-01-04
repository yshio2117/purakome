#!/bin/bash
pkill gunicorn
sudo nginx -s reload
gunicorn --bind 127.0.0.1:8000 django_app.wsgi -D

