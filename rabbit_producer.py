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


    message = "Hello World!"
    channel.basic_publish(exchange='',
                        routing_key='hello',
                        body=message)
    print(" [x] Sent '" + message + "'")
    connection.close()