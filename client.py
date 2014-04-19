#!/usr/bin/python

import sys, os, hashlib, StringIO
import bencode
import socket


# f = open(sys.argv[1], 'r')    
# contents = f.read()
# info_dict = bencode.bdecode(contents)
# #info_hash = util.sha1.hash(bencode.bencode(info_dict['info']))
# print bencode.bdecode(contents)


# Open torrent file
torrent_file = open(sys.argv[1], "rb")
metainfo = bencode.bdecode(torrent_file.read())
info = metainfo['info']
print hashlib.sha1(bencode.bencode(info)).hexdigest() 


s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 25159                # Reserve a port for your service.

s.connect((host, port))
print "connected."#s.recv(1024)
s.close                     # Close the socket when done