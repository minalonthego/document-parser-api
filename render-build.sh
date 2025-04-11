#!/usr/bin/env bash

# Install Tesseract
apt-get update && apt-get install -y tesseract-ocr

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
