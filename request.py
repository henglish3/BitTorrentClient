import StringIO
import struct
import binascii
import socket
import time
from message import WireMessage
from hashlib import sha1

class Request(object):
	i = 0
	end = 0
	length = 0
	last = 0
	debug = False
	s = socket.socket()
	pieces = ''
	path = '/Users/catjmp/Downloads/'
	file = ''

	@classmethod
	def __init__(cls, sock, num_pieces, piece_length, last_piece_length, deb, pie, name):
		cls.end = num_pieces
		cls.length = piece_length
		cls.last = last_piece_length
		cls.debug = deb
		cls.s = sock
		cls.pieces = StringIO.StringIO(pie)
		cls.file = open(cls.path + name, 'a+')
		return True

	@classmethod
	def message_handle(cls, buf):
		message = WireMessage.decode(buf)
		if cls.debug:print 'Decoded message: ' + str(message) #\n\t
		
		if message[0][0] == 'port':
			cls.s.send(WireMessage.construct_msg(2))
			return True
		
		if message[0][0] == 'choke':
			still_choked = True
			while still_choked:
				msg = cls.s.recv(5)
				if struct.unpack('!I', msg[5][0]) == 1:
					still_choked = False
			return True
		
		if message[0][0] == 'unchoke':
			print '\'Unchoke\' received. Requesting blocks!\n'
			cls.s.send(WireMessage.construct_msg(6, 0, 0, 16384))
			cls.i = 0
			return True
		
		if message[0][0] == 'piece':
			if cls.debug:
				print 'Block received!!! block size is: ' + str(len(buf))
				print 'A piece should be of size: ' + str(cls.length)
			actual_block = buf[13:]
			#I am working with a 16384 block size torrent, this won't work otherwise
			#I would need to set up another check to make sure cls.length was reached
			cls.i = cls.i + 1
			print 'Received ' + str(cls.i) + ' of ' + str(cls.end) + ' pieces'
			#verify
			piece_hash = sha1(actual_block).digest()
			if (piece_hash != cls.pieces.read(20)):
				print 'Corrupted'
			else:
				print 'Verified!'
				cls.file.write(actual_block)
				#out now, or at end
			if cls.i < cls.end - 1:
				cls.s.send(WireMessage.construct_msg(6, cls.i, 0, 16384))
			else:
				if cls.i == cls.end - 1:
					cls.s.send(WireMessage.construct_msg(6, cls.i, 0, cls.last))
				else: 
					cls.s.close()
					cls.file.close()
					print 'Exiting'
					return False
			return True
		
		if message[0][0] == 'keep_alive':
			cls.s.send('\x00')
			return True
		return True

	@classmethod
	def _read_pieces_hashes(cls, pieces):
		for i in range(0, len(pieces), 20):
			yield pieces[i:i+20]