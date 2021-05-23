FROM python:3.9.4-slim-buster
WORKDIR /gbdl

COPY requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt

COPY . .
COPY config_docker.yaml config.yaml
CMD ["python3", "-m", "flask", "run", "--no-reload", "--with-threads"]