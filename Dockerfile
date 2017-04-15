FROM python:3.5-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk add --no-cache --virtual .project-deps \
    gcc g++ \
    linux-headers \
    postgresql-dev \
    libjpeg-turbo-dev libpng-dev freetype-dev zlib-dev \
    ffmpeg \
    musl-dev

RUN ln -s /usr/bin/ffmpeg /usr/bin/avconv

ENV LIBRARY_PATH=/lib:/usr/lib

# pre-install slow things so we can edit requirements.txt without much pain
RUN pip install --no-cache-dir libsass==0.12.3

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

