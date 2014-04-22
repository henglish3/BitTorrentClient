import struct
import binascii
import socket
from message import WireMessage

class Request(object):
	
	@classmethod
	def message_handle(cls, buf, s):
		message = WireMessage.decode(buf)
		print message
		if message[0][0] == 'port':
			s.send(WireMessage.construct_msg(2))
			return True
		if message[0][0] == 'unchoke':
			print 'unchoked!! Time to request!'
			s.send(WireMessage.construct_msg(6, 0, 0, 16384))
			return True
		if message[0][0] == 'piece':
			print 'PIECE!!! maybe...'
			#s.send(WireMessage.construct_msg(6, 
			#blocks = 
			return True
		if message[0][0] == 'keep_alive':
			s.send('\x00')
			return True
		return False

	@classmethod
	def _read_pieces_hashes(cls, pieces):
		for i in range(0, len(pieces), 20):
			yield pieces[i:i+20]