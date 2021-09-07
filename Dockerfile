FROM python:3.8-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV MONGO_HOST=mongodb

ENV APP_ROOT=/home/app
ENV APP_HOME=/home/app/scrapper
ENV PYTHONPATH ${APP_ROOT}
RUN mkdir -p $APP_ROOT
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

RUN apk update && apk add --no-cache gcc git python3-dev musl-dev linux-headers \
    libc-dev  rsync zsh \
    findutils wget util-linux grep libxml2-dev libxslt-dev \
    &&  pip3 install --upgrade pip

RUN python -m pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
