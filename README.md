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
- [Docker](https://www.docker.com/get-started) - version 3.1.0 or higher
- Python 3.9. Use [pyenv](https://github.com/pyenv/pyenv) to easily switch Python versions.
- [Pipenv](https://pypi.org/project/pipenv/). Install by running `python -m pip install pipenv`

### Instructions for developing

1. From the base directory of the project, create a python3 virtual environment and activate it:
 ```sh
 ./tasks devenv
 pipenv shell
 ```
 
2. Run `./tasks validate` to run formatting, e2e tests and unit tests. This should be done before commiting.

### Troubleshooting

#### Checking dependencies fails locally due to pip

If running `./tasks check-deps` fails due to an outdated version of pip, yet works when running it in dojo (i.e. `./tasks dojo-deps`), then the local python environment containing pipenv may need to be updated (using pyenv instead of brew - to better control the pip version).
Ensure you have pyenv installed (use `brew install pyenv`).
Perform the following steps:

1. Run `brew uninstall pipenv`
2. Run `pyenv install <required-python-version>`
3. Follow step 3 from [here](https://github.com/pyenv/pyenv#basic-github-checkout )  
4. Run `pyenv global <required-python-version>`
5. For the following steps open another terminal.   
6. Run `python -m pip install pipenv` to install pipenv using the updated python environment.
7. Run `python -m pip install -U "pip>=<required-pip-version>"`
8. Now running `./tasks check-deps` should pass.
   - `pyenv global` should output the specific python version specified rather than `system`.
   - Both `python --version` and `pip --version` should point to the versions you have specified.
   - `ls -l $(which pipenv)` should output `.../.pyenv/shims/pipenv` rather than `...Cellar...` (which is a brew install).