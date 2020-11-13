FROM python:3.8-alpine

COPY s3-uploader/ s3-uploader/

RUN pip install tox

RUN apk add --no-cache bash git curl

RUN \
  curl https://dl.min.io/server/minio/release/linux-amd64/minio > /usr/bin/minio && \
  chmod +x /usr/bin/minio

RUN cd s3-uploader/ && python3 setup.py install

ENTRYPOINT sync-mesh-to-s3 --mesh-inbox $MESH_INBOX --s3-bucket $S3_BUCKET --state-file $STATE_FILE --s3-endpoint-url $S3_BUCKET_URL