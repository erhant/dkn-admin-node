import base64


def base64_to_json(data):
    """
    Convert base64 encoded data to JSON.

    :param data: Encoded data from Waku
    :return: JSON data
    """
    return base64.b64decode(data).decode('utf-8')


def str_to_base64(data):
    """
    Convert JSON data to base64 encoded data.

    :param data: Dumped data
    :return: Encoded data
    """
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')
