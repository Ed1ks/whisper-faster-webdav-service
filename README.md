# whisper-faster-webdav-service

## Description
This is an service for audio transcription on an different server, than those audio files are.
It connects with webdav (e.g. nexcloud, filerun,...), downloads audio files which are without .srt and transcribes them using whisper-faster to an .srt file and converts that to an .lrc file.
Both - the .srt and the .lrc files will be uploaded back to the webdav application.

This is an service meant to work in an docker container.

## Flow
1. Connect to WebDAV Application and get file list
2. Download all audio files which are without .srt, and download all .srt which are without .lrc
3. transcribe audio files
4. format all .srt file to .lrc
5. upload .srt and .lrc files

## Docker-Compose

see example in compose.yaml
