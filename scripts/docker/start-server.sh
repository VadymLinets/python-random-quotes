#!/bin/bash

if [[ "$SERVER" == "fastapi" || "$SERVER" == "litestar" || "$SERVER" == "starlette" ]]; then
  echo "Starting uvicorn server"
  exec uvicorn --host "0.0.0.0" --port 1140 --workers 4 app:app
elif [ "$SERVER" == "flask" ]; then
  echo "Starting gunicorn server"
  exec gunicorn -b "0.0.0.0:1140" -w 4 app:app
else
  echo "Starting gRPC server"
  exec python app.py
fi
