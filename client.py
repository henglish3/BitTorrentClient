#!/usr/bin/python

''' Authors: Harrison English, Brenden Leonard
	Bencode Library credit: Bram Cohen			(Read PKG-INFO file)
'''
import sys, os, hashlib, StringIO
import bencode
import socket
import struct
from random import choice
from hashlib import sha1
from message import WireMessage
from request import Request

debug = False
print chr(27) + '[2J' #clear terminal

# Open torrent file
torrent_file = open(sys.argv[1], 'rb')
metainfo = bencode.bdecode(torrent_file.read())
info = metainfo['info']
name = info['name']
piece_length = info['piece length']
total_length = info['length']
pieces = info['pieces']
pieces_hashes = list(Request._read_pieces_hashes(pieces))
num_pieces = len(pieces_hashes)
last_piece_length = total_length - (piece_length*(num_pieces - 1))
info_hash = hashlib.sha1(bencode.bencode(info)).digest()

'''Helpful print statements'''
print 'Beginning torrent for ' + name 
print 'Average piece length: ' + str(piece_length)
if debug:
	print 'The last piece will be of size: ' + str(last_piece_length)
print 'Total length: ' + str(total_length) 
print 'Number of pieces to receive: ' + str(num_pieces) + '\n'
'''////////////////////////''' 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname() # Get local machine name
'''host = 'bl_tardis'			'kate-english' - HE'''
port = 42044                # 25159 - HE
s.connect((host, port)) 	#connect to <host> at <port>

Request.__init__(s, num_pieces, piece_length, last_piece_length, debug, pieces, name) 

# Handshake
peer_id = ""
while len(peer_id) != 12:
	peer_id = peer_id + choice("1234567890")

peer_id = '-' + 'PY' + '0001' + '-' + peer_id
protocol_id = 'BitTorrent protocol'
# len_id = str(len(protocol_id))
reserved = '\x00'*7 + '\x01'
handshake = '\x13' + protocol_id + reserved + info_hash + peer_id

s.send(handshake)
data = s.recv(len(handshake))

if debug:
	print 'Handshake info:\n\t' + handshake
	print '\t' + str(data) + '\n'

buf = ''
msg = s.recv(5)
total_message_length, msg_id = struct.unpack("!IB", msg)
buf = msg
running = True

while running:
	try:
		if len(buf) == 0:
			msg = s.recv(5)
			buf = msg
		msg = buf[:5]
		if len(msg) == 4:
			total_message_length = struct.unpack('!I', msg)[0]
		else:	
			total_message_length, msg_id = struct.unpack('!IB', msg)
		if debug:
			print 'total message length: ' + str(total_message_length + 4)
			print 'buffer length before loop: ' + str(len(buf))
		while len(buf) < total_message_length + 4:
			try:
				msg = s.recv(4096)
			except Exception, e:
				print sys.exc_info()[0]
				break
			else:
				if len(msg) == 0: break
				buf += msg
				if debug: print 'buffer length in loop: ' + str(len(buf))
		buf1 = buf[:total_message_length + 4]
		buf = buf[(total_message_length + 4):]
		running = Request.message_handle(buf1)
	except Exception, e:
		print sys.exc_info()[0]
		break
	else:
		if len(msg) == 0: break

print 'EXIT'