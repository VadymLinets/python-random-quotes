#!/bin/sh

if [ "$SERVER" == "fastapi" ]; then
    echo "Starting uvicorn server"
    exec uvicorn --host "0.0.0.0" --port 1140 --workers 4 main:app
else
    echo "Starting gunicorn server"
    exec gunicorn -b "0.0.0.0:1140" -w 4 main:app
fi