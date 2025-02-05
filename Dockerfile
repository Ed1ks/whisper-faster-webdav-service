FROM python:3.11-slim-bullseye
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PUID=1000\
    PGID=1000

WORKDIR /whisper-faster-webdav-service
COPY . .
COPY requirements.txt ./

RUN pip install schedule faster-whisper easywebdav pysubs2
WORKDIR whisper-faster-webdav-service

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "Start.py"]
# Or enter the name of your unique directory and parameter set.

# sudo apt update
# sudo apt -y install python3.11 python3.11-distutils
# curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
# export PATH="$HOME/.local/bin:$PATH"
# pip install schedule faster-whisper easywebdav pysubs2

# check: AUD-20220206-WA0000.lrc & .srt
# check transcription AUD-20230730-WA0001.m4a