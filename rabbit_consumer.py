#!/usr/bin/env python
import pika
import logging
import ssl
import os

logging.basicConfig(level=logging.INFO)

conn_params = pika.ConnectionParameters(port=8080)

with pika.BlockingConnection(conn_params) as connection:
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(callback,
                        queue='hello',
                        no_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nExiting...")