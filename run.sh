#!/bin/bash
pip install -r requirements.txt
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload