import sys
import pika


conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = conn.channel()

channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or 'Hello World'
channel.basic_publish(exchange='', routing_key='hello', body=message,
                      properties=pika.BasicProperties(
                          delivery_mode=2))
print " [x] Sent %r" % (message,)

