import logging
from os.path import join
from signal import signal, SIGINT, SIGTERM
from sys import stdout

import boto3

from s3mesh.config import ForwarderConfig
from s3mesh.forwarder import build_forwarder_service, MeshConfig, S3Config

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def read_ssm_param(ssm, param_name):
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def write_file(contents, file_path):
    with open(file_path, "w") as f:
        f.write(contents)


def main():
    config = ForwarderConfig.from_environment_variables()

    ssm = boto3.client("ssm")

    mesh_client_cert_path = join(config.forwarder_home, "client_cert.pem")
    mesh_client_key_path = join(config.forwarder_home, "client_key.pem")
    mesh_ca_cert_path = join(config.forwarder_home, "ca_cert.pem")

    mesh_client_cert = read_ssm_param(ssm, config.mesh_client_cert_ssm_param_name)
    mesh_client_key = read_ssm_param(ssm, config.mesh_client_key_ssm_param_name)
    mesh_ca_cert = read_ssm_param(ssm, config.mesh_ca_cert_ssm_param_name)

    mesh_mailbox = read_ssm_param(ssm, config.mesh_mailbox_ssm_param_name)
    mesh_password = read_ssm_param(ssm, config.mesh_password_ssm_param_name)
    mesh_shared_key = read_ssm_param(ssm, config.mesh_shared_key_ssm_param_name)

    write_file(mesh_client_cert, mesh_client_cert_path)
    write_file(mesh_client_key, mesh_client_key_path)
    write_file(mesh_ca_cert, mesh_ca_cert_path)

    logging.basicConfig(stream=stdout, level=logging.INFO, format=LOG_FORMAT)

    forwarder_service = build_forwarder_service(
        mesh_config=MeshConfig(
            url=config.mesh_url,
            mailbox=mesh_mailbox,
            password=mesh_password,
            shared_key=bytes(mesh_shared_key, "utf-8"),
            client_cert_path=mesh_client_cert_path,
            client_key_path=mesh_client_key_path,
            ca_cert_path=mesh_ca_cert_path,
        ),
        s3_config=S3Config(bucket_name=config.s3_bucket_name, endpoint_url=None),
        poll_frequency_sec=int(config.poll_frequency),
    )

    def handle_sigterm(signum, frame):
        forwarder_service.stop()

    signal(SIGINT, handle_sigterm)
    signal(SIGTERM, handle_sigterm)

    forwarder_service.start()


if __name__ == "__main__":
    main()