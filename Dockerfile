FROM python:3.8-alpine

COPY . .

RUN \
  pip install tox

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
  apk add --no-cache bash git curl

RUN \
  curl https://dl.min.io/server/minio/release/linux-amd64/minio > /usr/bin/minio && \
  chmod +x /usr/bin/minio

CMD ["/bin/bash"]