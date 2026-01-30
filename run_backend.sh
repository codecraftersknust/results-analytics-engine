#!/bin/bash
# Run from project root
uvicorn src.api.main:app --reload --port 8000
