import logging

import pika

from src.rabbit.common import get_connection


class Producer:
    """
    A class to represent a RabbitMQ producer.

    Attributes:
    connection: A connection to the RabbitMQ server.
    channel: A channel to the RabbitMQ server.

    """

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        connection = get_connection()
        self.channel = connection.channel()

    def send_message(self, channel, message):
        """
        Send a message to the specified channel.

        Args:
            channel: The channel to send the message to.
            message: The message to send.
        """
        self.channel.basic_publish(
            exchange="",
            routing_key=channel,
            body=message.encode(),
            properties=pika.BasicProperties(delivery_mode=2),
        )  # 2 makes the message persistent
        logging.info("Task sent to the queue")
