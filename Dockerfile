# docker build -t ubuntu1604py36
FROM ubuntu:18.04

# RUN apt-get update && \
#   apt-get install -y software-properties-common && \
#   add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.8 python3.8-dev python3-pip python3.8-venv
RUN apt-get install -y git

# update pip
RUN python3.8 -m pip install pip --upgrade
RUN python3.8 -m pip install wheel

RUN apt-get update && apt-get install -y tesseract-ocr-eng

ADD requirements.txt /app/requirements.txt

WORKDIR /app/

RUN python3.8 -m pip install -r requirements.txt

RUN adduser --disabled-password --gecos '' app
