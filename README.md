# prm-gp2gp-mesh-s3-forwarder

Generic MESH to S3 forwarder, capable of reading messages from a MESH inbox and writing them to AWS S3.

## Running

Install with `python setup.py install`.

The MESH to S3 forwarder can then be started with `python -m s3mesh.entrypoint`.

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
| FORWARDER_HOME                  | Directory used to store certificates extracted from parameter store                                      |

## Developing

### Prerequistes
In order to get started with development, you will need Python - version 3.9 or higher.

To run the tests in the same container image used in the CI pipeline, you will need:
- [dojo](https://github.com/kudulab/dojo) 
- Docker - version 3.1.0 or higher

### Instructions for developing

1. From the base directory of the project, create a python3 virtual environment and activate it:
 ```sh
 ./tasks devenv
 source ./venv/bin/activate
 ```
 
2. Run `./tasks validate` to run formatting, e2e tests and unit tests. This should be done before commiting.
