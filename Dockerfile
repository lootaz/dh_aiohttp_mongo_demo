FROM python:3.6

RUN mkdir -p /usr/src
WORKDIR /usr/src

COPY requirements.txt /usr/src
RUN pip install -U -r requirements.txt
