from botocore.exceptions import ClientError


def build_client_error(**kwargs):
    error_message = kwargs.get("message", "test_message")
    operation = kwargs.get("operation", "test_operation")
    error_body = {"Error": {"Message": error_message}}

    return ClientError(error_body, operation)
