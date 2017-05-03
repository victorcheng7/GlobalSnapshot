#!/usr/bin/env python

import socket
import time
import threading
import sys
import Queue
import copy

# argv accept input file, python asg2.py 1 setup.txt site1.txt
def main():
	if(len(sys.argv) != 4):
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
		for line in f.readlines():
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
				if dest_id == site.id:
					site.addIncomingChannel(source_id)
	site.openOutgoingChannels()

def execute_commands(site, command_file):
	#Read command file. ex - site1.txt
	with open(command_file, 'r') as f:
		for command in f.readlines():
			command = command.lower().strip()
			site.execute(command)

class Message(object):
	MARKER = "M"
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
		self.snap_count = 0
		self.balance = 10
		self.incoming_channels = {}
		self.addr_book = []
		self.outgoing_channels = {}
		self.incomingChannel = None
		self.snapID_table = {}

	def openIncomingChannel(self, IP, port):
		self.incomingChannel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.incomingChannel.bind( (IP, port) )
		self.incomingChannel.setblocking(0) 
		self.incomingChannel.listen(1)

	def addOutgoingChannel(self, dest_id):
		self.outgoing_channels[dest_id] = None

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
		self.incoming_channels[source_id] = [0, False]

	def execute(self, command):
		self.checkIncomingMsgs()
		keyWords = command.split()
		if "send" == keyWords[0]:
			dest_id = int(keyWords[1])
			amount = int(keyWords[2])
			self.sendMoney(dest_id, amount)
		elif "snapshot" == keyWords[0]:
			self.startSnapshot()
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
					if msg.snap_id not in self.snapID_table: #First Marker -> input into snapID_table
						counter = 1
						site_state = self.balance #Take Local State Snapshot
						incoming_channels_states = copy.deepcopy(self.incoming_channels)
						self.snapID_table[msg.snap_id] = [counter, site_state, incoming_channels_states]
						self.snapID_table[msg.snap_id][2][msg.source_id][0] = True #Shut down the incoming channel of 1st Marker
						self.sendMarkers(msg.snap_id)
					else: #Not the first marker
						self.snapID_table[msg.snap_id][0] += 1 #increase counter by 1
						self.snapID_table[msg.snap_id][2][msg.source_id][0] = True #Take no more Snapshot on the channel
						if self.snapID_table[msg.snap_id][0] == len(self.incoming_channels): #Received all markers
							self.outputLocalSnapshotAt(msg.snap_id)
				else: #received a msg
					self.balance += msg.amount #Fix the real-time balance
					for _, v in enumerate(self.snapID_table):
						if v[0] == len(self.incoming_channels): #Finished Snapshot
							continue
						if v[2][msg.source_id][0] == False: #The current money message is before Marker
							v[2][msg.source_id][1] += msg.amount #Record the increase in amount
			except Exception:
				break

	def outputLocalSnapshotAt(self, snap_id):
		output = snap_id + ": "
		output += str(self.snapID_table[snap_id][1]) + " "
		l = self.snapID_table[snap_id][2].items()
		sorted(l, key=lambda item: item[0])
		for _, val in l:
			output += str(val) + " "
		output = output.strip()
		print output
		del self.snapID_table[snap_id]

	def sendMoney(self, dest_id, amount):
		msg = Message(self.id, None, amount)
		self.outgoing_channels[dest_id].send(str(msg))

	def sendMarkers(self, snap_id):
		msg = Message(self.id, snap_id, None, is_marker = True)
		for _, sock in enumerate(self.outgoing_channels):
			sock.send(str(msg))

	def startSnapshot(self):
		self.snap_count += 1
		counter = 0
		snap_id = str(self.id) + "." + str(self.snap_count)
		site_state = self.balance #Take Local State Snapshot
		incoming_channels_states = copy.deepcopy(self.incoming_channels)
		self.snapID_table[snap_id] = [counter, site_state, incoming_channels_states]
		self.sendMarkers(snap_id)

	def sleep(self, amount):
		count = (amount * 1000)/200
		i = 0
		while(i < count):
			time.sleep(0.2)
			self.checkIncomingMsgs()
			i += 1

if __name__ == "__main__":
	main()