import sys
import pika


conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = conn.channel()

channel.queue_declare(queue='hello')

message = ' '.join(sys.argv[1:]) or 'Hello World'

