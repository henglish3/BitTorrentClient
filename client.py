#!/usr/bin/python

import sys, os, hashlib, StringIO
import bencode
import socket
from random import choice
from hashlib import sha1


# f = open(sys.argv[1], 'r')    
# contents = f.read()
# info_dict = bencode.bdecode(contents)
# #info_hash = util.sha1.hash(bencode.bencode(info_dict['info']))
# print bencode.bdecode(contents)


# Open torrent file
torrent_file = open(sys.argv[1], "rb")
metainfo = bencode.bdecode(torrent_file.read())
info = metainfo['info']
info_hash = hashlib.sha1(bencode.bencode(info)).hexdigest() 
print hashlib.sha1(bencode.bencode(info)).hexdigest() 

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 42044                # 25159 - HE; Reserve a port for your service.

s.connect((host, port))
print "connected."
#s.close()	 # Close the socket when done

# Handshake
peer_id = ""
while len(peer_id) != 12:
	peer_id = peer_id + choice("1234567890")

peer_id = "-" + "PY" + "0001" + "-" + peer_id
protocol_id = "BitTorrent protocol"
len_id = str(len(protocol_id))
reserved = "00000000"
handshake = len_id + protocol_id + reserved + info_hash + peer_id
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((host, port))
print handshake
s.send(handshake)
data = s.recv(len(handshake))
print data
s.close()
#end handshake and begin asking for pieces


	# return data                  