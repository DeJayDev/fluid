FROM python:3

WORKDIR /home/fluid

RUN apt-get update && apt-get install -y git youtube-dl ffmpeg

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m", "disco.cli"]
