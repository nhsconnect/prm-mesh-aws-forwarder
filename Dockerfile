FROM python:3.8-alpine

COPY s3-uploader/ s3-uploader/

RUN pip install tox

RUN apk add --no-cache bash git curl

RUN \
  curl https://dl.min.io/server/minio/release/linux-amd64/minio > /usr/bin/minio && \
  chmod +x /usr/bin/minio

RUN cd s3-uploader/ && python3 setup.py install

RUN touch /var/log/cron.log

RUN (crontab -l ; echo "*/1 * * * * echo "Hello world" >> /var/log/cron.log") | crontab

CMD ["/bin/bash", "cron && tail -f /var/log/cron.log"]