#!/usr/bin/env python
import pika
import logging
import ssl
import os
import sys
import getopt


def usage():
    print "Usage: " + sys.argv[0] + " [options]"
    print "  -h --help: Shows this window"
    print "  -p --port: "
    print "  -e --exchange: "
    print "  -s --severity: "
    print "  -m --message: "
    print "  -o --host: "

try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:e:s:m:o:", ["help", "port=", "exchange=", "severity=", "message=", "host="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err)  # will print something like "option -a not recognized"
    usage()
    exit(2)

port=5671
queue_name = ""
severity = "info"
message = "Hello world!"
message = "Hello world!"
exchange = "test"
host = "localhost"

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        exit()
    elif o in ("-p", "--port"):
        port = int(a)
    elif o in ("-e", "--exchange"):
        exchange = a
    elif o in ("-s", "--severity"):
        severity = a
    elif o in ("-m", "--message"):
        message = a
    elif o in ("-o", "--host"):
        host = a
    else:
        assert False, "unhandled option"

logging.basicConfig(level=logging.WARNING)

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

    publish_opts = pika.BasicProperties(delivery_mode = 2)
    channel.basic_publish(exchange=exchange, routing_key=severity, body=message, properties=publish_opts)

    print(" [x] Sent '" + message + "' with severity '" + severity + "' to exchange '" + exchange + "'")
    connection.close()