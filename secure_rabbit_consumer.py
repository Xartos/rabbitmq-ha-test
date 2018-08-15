#!/usr/bin/env python
import pika
import logging
import ssl
import os
import sys
import time
import getopt


def usage():
    print "Usage: " + sys.argv[0] + " [options]"
    print "  -h --help: Shows this window"
    print "  -p --port: "
    print "  -q --queue: "
    print "  -e --exchange: "
    print "  -s --severities: "
    print "  -o --host: "

try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:q:s:e:o:", ["help", "port=", "queue=", "severities=", "exchange=", "host="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err)  # will print something like "option -a not recognized"
    usage()
    exit(2)

port=5671
queue_name = ""
severities = None
exchange = "test"
host = "localhost"

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        exit()
    elif o in ("-p", "--port"):
        port = int(a)
    elif o in ("-q", "--queue"):
        queue_name = a
    elif o in ("-e", "--exchange"):
        exchange = a
    elif o in ("-o", "--host"):
        host = a
    elif o in ("-s", "--severities"):
        severities = map(str.strip, a.split(","))
    else:
        assert False, "unhandled option"

logging.basicConfig(level=logging.WARNING)

if not severities:
    print "Error: severities must be set"
    usage()
    exit(1)

ca_cert_path = os.path.abspath("testca/cacert.pem")
key_path = os.path.abspath("client/key.pem")
cert_path = os.path.abspath("client/cert.pem")

ssl_opts = {
    "ssl_version": ssl.PROTOCOL_TLSv1,
    "ca_certs": ca_cert_path,
    "keyfile": key_path,
    "certfile": cert_path,
    "cert_reqs": ssl.CERT_REQUIRED
}

conn_params = pika.ConnectionParameters(host=host, port=port, ssl=True, ssl_options=ssl_opts)

with pika.BlockingConnection(conn_params) as connection:
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type='direct')
    result = channel.queue_declare(queue=queue_name, exclusive=(not queue_name), durable=True)
    queue_name = result.method.queue

    for severity in severities:
        channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=severity)

    def callback(ch, method, properties, body):
        print(" [|] %r:%r queue %s" % (method.routing_key, body, queue_name))
        num_dots = body.count('.')
        print(" [|] Working for %d s" % num_dots)
        time.sleep(num_dots)
        print " [x] Done"
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(callback, queue=queue_name)

    print " [|] Connecting to '%s:%d'" % (host, port)
    print " [|] Using exchange '" + exchange + "' and queue '" + queue_name + "' and binding to '" + ", ".join(severities) + "'"
    print(' [*] Waiting for messages. To exit press CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nExiting...")