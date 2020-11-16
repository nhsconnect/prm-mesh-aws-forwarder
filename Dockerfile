FROM python:3.8-alpine

COPY s3-uploader/ s3-uploader/

RUN cd s3-uploader/ && python3 setup.py install

ENTRYPOINT sync-mesh-to-s3 --mesh-inbox $MESH_INBOX --s3-bucket $S3_BUCKET --state-file $STATE_FILE