FROM node:14-buster-slim
WORKDIR /gbmm
COPY . .
RUN npm install
RUN npm run build

FROM python:3.9.4-slim-buster
WORKDIR /gbmm
ENV FLASK_APP=server.app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt
COPY --from=0 /gbmm .
COPY config_docker.yaml config.yaml

CMD ["python3", "-m", "flask", "run", "--no-reload", "--with-threads"]