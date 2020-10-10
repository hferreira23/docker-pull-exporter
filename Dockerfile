FROM python:alpine

RUN apk update && \
    apk upgrade --available && \
    sync && \
    apk add curl bash build-base yaml-dev && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/* /var/cache/distfiles/*

RUN python3 -m pip install --no-cache-dir --no-binary PyYAML PyYAML

RUN python3 -m pip install requests prometheus_client uwsgi

COPY src/* /opt/docker_pull_exporter

EXPOSE 2004

ENTRYPOINT ["uwsgi", "--ini", "/opt/docker_pull_exporter/docker_pull_exporter.ini"]
