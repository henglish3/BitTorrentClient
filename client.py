#!/usr/bin/python

import sys, os, hashlib, StringIO
import bencode
import socket
import struct
import time
from random import choice
from hashlib import sha1
from message import WireMessage
from request import Request

# Open torrent file
torrent_file = open(sys.argv[1], "rb")
metainfo = bencode.bdecode(torrent_file.read())
info = metainfo["info"]
piece_length = metainfo['info']['piece length']
print piece_length
pieces = metainfo['info']['pieces']
pieces_hashes = list(Request._read_pieces_hashes(pieces))
num_pieces = len(pieces_hashes)
print num_pieces
info_hash = hashlib.sha1(bencode.bencode(info)).digest() 

#s = socket.socket()         # Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname() # Get local machine name
port = 42044                # 25159 - HE; Reserve a port for your service.

s.connect(("128.61.66.128", 25159)) #"bl-tardis", 42044))   #"kate-english", 25159))
# print "connected to " + host

# Handshake
peer_id = ""
while len(peer_id) != 12:
	peer_id = peer_id + choice("1234567890")

peer_id = '-' + 'PY' + '0001' + '-' + peer_id
protocol_id = 'BitTorrent protocol'
# len_id = str(len(protocol_id))
reserved = '\x00'*7 + '\x01'
handshake = '\x13' + protocol_id + reserved + info_hash + peer_id

print 'Handshake info\n' + handshake
s.send(handshake)
data = s.recv(len(handshake))
print data
buf = ""
msg = s.recv(5)
total_message_length, msg_id = struct.unpack("!IB", msg)
buf = msg

while True:
	try:
		if len(buf) == 0:
			msg = s.recv(5)
			buf = msg
		msg = buf[:5]
		if len(msg) == 4:
			total_message_length = struct.unpack("!I", msg)[0]
		else:	
			total_message_length, msg_id = struct.unpack("!IB", msg)
		print 'total message length: ' + str(total_message_length)
		print "buffer length before loop: " + str(len(buf))
		while len(buf) < total_message_length + 4:
			try:
				msg = s.recv(4096)
			except Exception, e:
				print sys.exc_info()[0]
				break
			else:
				if len(msg) == 0: break
				buf += msg
				print "buffer length in loop: " + str(len(buf))
		buf1 = buf[:total_message_length + 4]
		buf = buf[(total_message_length + 4):]
		Request.message_handle(buf1, s)
	except Exception, e:
		print sys.exc_info()[0]
		break
	else:
		if len(msg) == 0: break

print "EXIT"

s.close()
# end handshake and begin asking for pieces