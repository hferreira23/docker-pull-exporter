FROM python:alpine as base

FROM base as builder

RUN apk update && \
    apk upgrade --available && \
    sync && \
    apk add curl bash musl-dev gcc libc-dev yaml-dev linux-headers && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/* /var/cache/distfiles/*

RUN python3 -m pip install --prefix="/build" --no-cache-dir --no-binary PyYAML PyYAML

RUN python3 -m pip install --prefix="/build" requests prometheus_client uwsgi

FROM base

RUN addgroup -S -g 2004 docker_pull_exporter && \
    adduser -S -H -D -s /bin/bash -u 2004 docker_pull_exporter

COPY --from=builder /build /usr/local
COPY src/* /opt/docker_pull_exporter/

EXPOSE 2004

ENTRYPOINT ["uwsgi", "--ini", "/opt/docker_pull_exporter/docker_pull_exporter.ini"]
