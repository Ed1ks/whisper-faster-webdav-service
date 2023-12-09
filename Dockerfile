FROM python:3.11

RUN pip install schedule faster-whisper easywebdav pysubs2
WORKDIR whisper-faster-webdav-service
CMD ["python", "Start.py"]
# Or enter the name of your unique directory and parameter set.

# sudo apt update
# sudo apt -y install python3.11 python3.11-distutils
# curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
# export PATH="$HOME/.local/bin:$PATH"
# pip install schedule faster-whisper easywebdav pysubs2

# check: AUD-20220206-WA0000.lrc & .srt
# check transcription AUD-20230730-WA0001.m4a