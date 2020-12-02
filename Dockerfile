FROM python:3.8-alpine

ENV POLL_FREQUENCY=60
ENV FORWARDER_HOME=/mesh-forwarder

RUN addgroup --system mesh && adduser --ingroup mesh --system mesh

COPY . /mesh-forwarder

RUN cd /mesh-forwarder && python setup.py install

RUN chown -R mesh:mesh /mesh-forwarder

USER mesh

ENTRYPOINT ["python", "/mesh-forwarder/entrypoint.py"]