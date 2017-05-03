#!/usr/bin/env python2

import socket
import time
import threading
import sys
import Queue

# argv accept input file, python asg2.py 1 setup.txt site1.txt
def main():
	if(len(sys.argv) != 3):
	    print("USAGE: python [site_id] [setup_file] [command_file]")
	    exit(1)
    site_id = int(sys.argv[1])
    site = Site(site_id)
    setup_file = sys.argv[2]
    command_file = sys.argv[3]
	setup(site, setup_file)
	execute_commands(site, command_file)

def setup(site, setup_file):
	#Read setup file. ex - setup.txt     
	with open(setup_file, 'r') as f:
    	N = int(f.readline().strip())
 	   	process_id = 0
 	   	for line in f.readLines():
 	   		process_id += 1
 	   		if process_id <= N:
 	   			IP, port = line.strip().split()
 	   			port = int(port)
 	   			site.addr_book.append( (IP, port) )
 	   			if process_id == site.id:
 	   				site.openIncomingChannel( IP, port ) #open for traffic
 	   		else:
	 	   		source_id, dest_id = line.strip().split()
				if source_id == site.id:
					site.addOutgoingChannel(dest_id) #only need to connect to outgoing channels
                if dest_id == site_id:
                    site.addIncomingChannel(source_id)
	site.openOutgoingChannel()

def execute_commands(site, command_file):
	#Read command file. ex - site1.txt
	with open(command_file, 'r') as f:
		for command in f.readlines():
			command = command.lower().strip()
            site.execute(command)

class Message(object):
	MARKER = "M"
    NO_SNAPSHOT = "0.0"
	def __init__(self, source_id, snap_id, amount, is_marker = False):
		self.source_id = source_id
        self.snap_id = snap_id
        self.amount = amount
		self.is_marker = is_marker

	def __str__(self):
		if self.is_marker:
			return str(source_id) + " " + str(snap_id) + " " + Message.MARKER 
		else:
			return str(source_id) + " " + str(snap_id) + " " + str(amount)

	def __repr__(self):
		return __str__(self)

	@staticmethod
	def reconstructFromString(str):
		keyWords = str.strip().split()
		source_id = int(keyWords[0])
        snap_id = keyWords[1]
		if keyWords[2] == Message.MARKER:
			return Message(source_id, snap_id, None, is_marker = True)
		else:
			amount = int(keyWords[2])
			return Message(source_id, snap_id, amount)

class Site(object):
	def __init__(self, site_id):
		self.id = site_id
		self.balance = 10
        self.incoming_channels = {}
		self.addr_book = []
		self.outgoing_channels = {}
		self.incomingChannel = None

	def openIncomingChannel(self, IP, port):
		self.incomingChannel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.incomingChannel.bind( (IP, port) )
        self.incomingChannel.setblocking(0) 
		self.incomingChannel.listen(1)

	def addOutgoingChannel(self, dest_id):
		self.outgoing_channels.put(dest_id, None)

	def openOutgoingChannels(self):
		time.sleep(5) #To make sure all other processes are up
		for dest_id, _ in enumerate( self.outgoing_channels ):
    		self.outgoing_channels[dest_id] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while True:
                try:
                    self.outgoing_channels[dest_id].connect(self.addr_book[dest_id - 1])
                    break
                except Exception:
                    time.sleep(1)

    def addIncomingChannel(self, source_id):
        self.incoming_channels[source_id] = 0

    def execute(self, command):
		self.checkIncomingMsgs()
		keyWords = command.split()
		if "send" == keyWords[0]:
			dest_id = int(keyWords[1])
			amount = int(keyWords[2])
			self.sendMoney(dest_id, amount)
		elif "snapshot" == keyWords[0]:
			startSnapshot()
		elif "sleep" == keyWords[0]:
			time = float(keyWords[1])
			self.sleep(time)
		else:
			print "CANNOT RECOGNIZE THE COMMAND: " + command
			exit(1)
		self.checkIncomingMsgs()

	def checkIncomingMsgs(self):
        BUF_SIZE = 1024
        while True:
            try:
                con, addr = self.incomingChannel.accept()
                msg = con.recv(BUF_SIZE)
                msg = Message.reconstructFromString(msg.strip())
                if(msg.is_marker):
                    if(msg.initiator_id == site_id)
                        #increment counter++ 
                        #if this counter == global counter, snapshot ends and print
                        #source_id... log all future incoming messages as channel state
                    else:
                        #send this marker to all outgoing channels and your own site_id
                else:
                    #money transfer
            except Exception:
                break

	def sendMoney(self, dest_id, amount):
		msg = Message(self.id, amount)
		outgoing_channels[dest_id].send(str(msg))

	def startSnapshot(self):
        #Initiate message that contains your site_id as initiator_id to all outgoing channels
	
    def sleep(self, amount):
		count = (amount * 1000)/200
		i = 0
		while(i < count):
			time.sleep(0.2)
			self.checkIncomingMsgs()
			i += 1
	
if __name__ == "__main__":
	main()