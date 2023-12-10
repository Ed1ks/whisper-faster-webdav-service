# whisper-faster-webdav-service

## Description
This is an service for audio transcription on an different server, than those audio files are.
It connects with webdav (e.g. nexcloud, filerun,...), downloads audio files which are without .srt and transcribes them using whisper-faster to an .srt file and converts that to an .lrc file.
Both - the .srt and the .lrc files will be uploaded back to the webdav application.

This is an service meant to work in an docker container, but will also work on any linux distribution.

Feel free to change the code to your needs.

## Flow
1. Connect to WebDAV Application and get file list
2. Download all audio files which are without .srt, and download all .srt which are without .lrc
3. transcribe audio files
4. format all .srt file to .lrc
5. upload .srt and .lrc files

## Docker-Compose

see example in compose.yaml

## How To Install
1. use docker-compose so the whisper-faster-webdav-service will be created
2. upload all .py files inside this volume
   
   2.5. you can tweak settings for transcription inside of Start.py (e.g. cpu cores, gpu etc.)
   
   2.6. you can create an .env file in this volume, or else use docker compose
4. restart container
