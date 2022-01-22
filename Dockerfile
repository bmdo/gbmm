FROM node:14-buster-slim
WORKDIR /gbmm
COPY . .
RUN npm install
RUN npm run build

FROM python:3.9.4-slim-buster
WORKDIR /gbmm
ENV FLASK_APP=server.app
ENV GBMM_ROOT='/app'
ENV GBMM_FILES='/data'
COPY requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt
COPY --from=0 /gbmm .

EXPOSE 5000/tcp

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8877"]