import pika
import logging
from config import Config


def setup_rabbitmq_connection():
    try:
        connection = pika.BlockingConnection(
            pika.URLParameters(Config.RABBITMQ_URL))
        return connection
    except Exception as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")
        return None

# publish an event to queue


def publish_event(exchange_name, routing_key, message):
    connection = setup_rabbitmq_connection()

    if not connection:
        return None

    try:
        channel = connection.channel()
        channel.exchange_declare(
            exchange=exchange_name, exchange_type='direct')
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        logging.info(
            f"Published message to exchange {exchange_name} with routing key {routing_key}: {message}")
    finally:
        connection.close()


# listen to events sent from different microservice
def consume_events(on_message_received):
    connection = setup_rabbitmq_connection()

    if not connection:
        return None

    try:
        channel = connection.channel()
        channel.exchange_declare(
            exchange='event_exchange', exchange_type='direct')
        channel.queue_declare(queue='order_service_queue')

        # bind the queues to routing keys for listening to user and product related events
        channel.queue_bind(exchange='event_exchange',
                           queue='order_service_queue', routing_key='user.registered')
        channel.queue_bind(exchange='event_exchange',
                           queue='order_service_queue', routing_key='user.profile.updated')
        channel.queue_bind(exchange='event_exchange',
                           queue='order_service_queue', routing_key='product.created')

        # Set up the consumer to listen for messages
        channel.basic_consume(queue='order_service_queue',
                              on_message_callback=on_message_received, auto_ack=True)
        logging.info(
            "Waiting for `user.updated` and `product.created` events. To exit press CTRL+C")
        channel.start_consuming()

    finally:
        connection.close()
