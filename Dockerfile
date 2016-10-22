FROM python:3.6-alpine
MAINTAINER Xavier Barbosa <clint.northwood@gmail.com>

ENV CONSUL_VERSION 0.7.0

RUN set -ex \
	&& apk add --no-cache --virtual .fetch-deps \
		openssl \
		unzip \
  && wget https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip \
  && unzip -d /usr/local/bin consul_${CONSUL_VERSION}_linux_amd64.zip \
  && chmod 0755 /usr/local/bin/consul \
  && rm -f consul_${CONSUL_VERSION}_linux_amd64.zip \
  && apk del .fetch-deps

WORKDIR /app
ADD requirements-tests.txt /app/
RUN python -m pip install -r requirements-tests.txt
RUN apk add --no-cache make bash
