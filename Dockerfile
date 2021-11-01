#FROM python:3.9-alpine

#WORKDIR /work
#COPY app /work/app
#COPY tests /work/tests
#COPY db /work/db
#COPY data /work/data
#COPY requirements.txt /work/requirements.txt
#
#RUN pip install -r requirements.txt
#
#CMD [""]

FROM python:3.9.5-alpine3.13

RUN apk update \
    && apk upgrade \
    && apk add --no-cache bash \
    && apk add --no-cache --virtual=build-dependencies unzip \
    && apk add --no-cache curl \
    && apk add --no-cache openjdk8-jre \
    && apk add --no-cache musl-dev gcc libffi-dev g++ \
    && apk add py3-numpy py3-scipy py3-pandas py3-bcrypt


### 3. Get Python, PIP

#RUN apk add --no-cache python3 py3-pip python3-dev \
#    && python3 -m ensurepip \
#    && pip3 install --upgrade pip setuptools \
#    && rm -r /usr/lib/python*/ensurepip \
#    && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
#    && if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
#    && rm -r /root/.cache

#RUN apk add --no-cache musl-dev gcc libffi-dev g++

WORKDIR /work

#COPY app /work/app
#COPY tests /work/tests
#COPY db /work/db
#COPY data /work/data
COPY requirements.txt /work/requirements.txt
#COPY runtests.sh /work/runtests.sh

RUN pip install -r requirements.txt

ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

#CMD ["./runtests.sh"]
