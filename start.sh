#!/usr/bin/env bash
gunicorn --workers 8 --bind 127.0.0.1:8080 wsgi:app
