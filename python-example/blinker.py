from blinker import signal
from blinker.base import Signal

ready = signal('ready')
def substriber(sender):
	print ("Got a signal sent by %r" % sender)

