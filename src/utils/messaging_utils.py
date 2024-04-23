import base64
import json


def base64_to_json(data):
    """
    Convert base64 encoded data to JSON.

    :param data: Encoded data from Waku
    :return: JSON data
    """
    return json.loads(base64.b64decode(data).decode('utf-8'))


def json_to_base64(data):
    """
    Convert JSON data to base64 encoded data.

    :param data: JSON data
    :return: Encoded data
    """
    return base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')


def job_to_base64(signature, data):
    """
    Convert job data to a publishable format.

    :param signature: Signature of Admin Node
    :param data: Job data
    :return:
    """

    return base64.b64encode(signature + json.dumps(data).encode('utf-8')).decode('utf-8')
