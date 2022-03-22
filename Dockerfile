FROM python:3.9.7-buster

WORKDIR /work

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache -r requirements.txt

RUN apt-get update && apt-get install -y openjdk-11-jre

COPY app ./app
COPY data ./data
COPY db/mysql ./db/mysql
COPY .env ./.env

ENV JAVA_HOME=/usr/lib/jvm/openjdk-11-jdk
ENV PATH=$PATH:$JAVA_HOME/bin
ENV PYTHONPATH="${PYTHONPATH}:${PWD}"

CMD ["python", "-m", "app.consume.kinesis", "--delay", "2.0"]