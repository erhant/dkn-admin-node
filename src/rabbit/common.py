import ssl

import pika

from src.config import Config

settings = Config()


def get_connection():
    """
    Get a connection to the RabbitMQ server.

    Returns:
        A connection to the RabbitMQ server.

    """

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_ciphers("ECDHE+AESGCM:!ECDSA")
    ssl_option = pika.SSLOptions(ssl_context, "localhost")
    credentials = pika.PlainCredentials(settings.RABBITMQ_USERNAME, settings.RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, heartbeat=600,
                                       blocked_connection_timeout=300, connection_attempts=5,
                                       ssl_options=ssl_option, credentials=credentials, virtual_host="/")
    connection = pika.BlockingConnection(params)
    return connection


def create_queue(channel, q_name):
    """
    Create a queue with the specified name.

    Args:
        channel: The channel to create the queue on.
        q_name: The name of the queue to create.

    """
    channel.queue_declare(queue=q_name)
