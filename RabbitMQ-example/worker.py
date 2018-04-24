import time
import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')


def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    time.sleep(body.count('.'))
    print " [x] Done."
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(callback, queue='hello')

print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()
