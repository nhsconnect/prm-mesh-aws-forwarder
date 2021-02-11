# prm-gp2gp-mesh-s3-forwarder

Generic MESH to S3 forwarder, capable of reading messages from a MESH inbox and writing them to AWS S3.

## Checks before committing

Run the following commands: `./tasks validate` to run formatting, e2e tests and unit tests before committing.

## Running

Install with `python setup.py install`.

The MESH to S3 forwarder can then be started with `python -m s3mesh.entrypoint`

Running the forwarder requires the following environment variables to be set:

| Environment variable            | Description                                                                                             | 
| ------------------------------- | ------------------------------------------------------------------------------------------------------- |
| MESH_URL                        | URL of MESH endpoint to connect to                                                                      |
| MESH_MAILBOX_SSM_PARAM_NAME     | Name of AWS SSM parameter store entry containing the name of the MESH inbox to consume messages from    |
| MESH_PASSWORD_SSM_PARAM_NAME    | Name of AWS SSM parameter store entry containing the password of the MESH inbox to consume message from |
| MESH_SHARED_KEY_SSM_PARAM_NAME  | Name of AWS SSM parameter store entry containing the MESH shared key                                    |
| MESH_CLIENT_CERT_SSM_PARAM_NAME | Name of AWS SSM parameter store entry containing the client certificate                                 |
| MESH_CLIENT_KEY_SSM_PARAM_NAME  | Name of AWS SSM parameter store entry containing the client certificate key                             |
| MESH_CA_CERT_SSM_PARAM_NAME     | Name of AWS SSM parameter store entry containing the certificate authority chain                        |
| S3_BUCKET_NAME                  | S3 bucket to publish messages to                                                                        |
| POLL_FREQUENCY                  | Duration in seconds between each poll of the mesh mailbox                                               |
| FORWARDER_HOME                  | Directory used to store certifcates extracted from parameter store                                      |
