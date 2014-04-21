#!/usr/bin/python

import sys, os, hashlib, StringIO
import bencode
import socket
from random import choice
from hashlib import sha1
from message import WireMessage

# Open torrent file
torrent_file = open(sys.argv[1], "rb")
metainfo = bencode.bdecode(torrent_file.read())
info = metainfo["info"]
info_hash = hashlib.sha1(bencode.bencode(info)).digest() 
print info_hash
print len(info_hash)

# s = socket.socket()         # Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname() # Get local machine name
port = 42044                # 25159 - HE; Reserve a port for your service.

s.connect(("128.61.23.192", 42044))#"bl-tardis", 42044))   #"kate-english", 25159))
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

print handshake
s.send(handshake)
data = s.recv(len(handshake))
print data

buf = ""
loop = 1
while True:
	try:
		print loop
		msg = s.recv(4096)
# 		print WireMessage.decode(msg)
	except Exception, e:
		break
	else:
		if len(msg) == 0: break
		buf += msg
		print "buf" + buf
		loop += 1

print "EXIT"		
# if len(buf) == 0: return False
# print WireMessage.decode_all(buf)
print WireMessage.decode(buf)




s.close()
# end handshake and begin asking for pieces
