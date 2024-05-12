import json
import logging

from src.rabbit.common import get_connection


class Consumer:
    """
    A class to represent a RabbitMQ consumer.

    Attributes:
    connection: A connection to the RabbitMQ server.
    channel: A channel to the RabbitMQ server.


    """

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        connection = get_connection()
        self.channel = connection.channel()

    def receive_message(self, queue, n=1):
        """
        Receive 'n' messages from the specified queue.

        Args:
            queue: The queue to receive messages from.
            n: The number of messages to receive. Default is 1.

        """

        message_count = 0
        tasks = []

        def callback(ch, method, properties, body):
            nonlocal message_count
            message_count += 1
            logging.info(f"Received Message {message_count}: {body}")

            # Acknowledge that the message has been received
            ch.basic_ack(delivery_tag=method.delivery_tag)

            # Stop consuming after 'n' messages
            if message_count >= n:
                ch.stop_consuming()
            json_loaded = json.loads(body.decode("utf-8"))
            tasks.append(json_loaded)

        # Tell RabbitMQ that this particular callback function should receive messages from our 'hello' queue
        self.channel.basic_consume(
            queue=queue, on_message_callback=callback, auto_ack=False
        )

        self.channel.start_consuming()
        return tasks[0]

    def receive_questions(self, queue, n=1):
        """
        Receive 'n' messages from the specified queue.

        Args:
            queue: The queue to receive messages from.
            n: The number of messages to receive. Default is 1.

        """

        message_count = 0
        tasks = []

        def callback(ch, method, properties, body):
            nonlocal message_count
            message_count += 1
            logging.info(f"Received Message {message_count}: {body}")

            # Acknowledge that the message has been received
            ch.basic_ack(delivery_tag=method.delivery_tag)

            # Stop consuming after 'n' messages
            if message_count >= n:
                ch.stop_consuming()
            json_loaded = json.loads(body.decode("utf-8"))
            tasks.append(json_loaded)

        # Tell RabbitMQ that this particular callback function should receive messages from our 'hello' queue
        self.channel.basic_consume(
            queue=queue, on_message_callback=callback, auto_ack=False
        )

        self.channel.start_consuming()
        return tasks[0]


