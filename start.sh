#!/bin/bash

echo "Installing dependencies..."

pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port $PORT
