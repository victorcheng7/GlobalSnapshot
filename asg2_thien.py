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

'''
def listenThread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, port))
    sock.listen(10)

    while True:
        stream, addr = sock.accept()
        data = stream.recv(1024)
        q.put(int(data))
        stream.close()
    '''
#CAUTION - Don't block. Check incoming communiation streams before/after processing every command

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
	site.openOutgoingChannel()

    # num_line = 0
    # num_sites = 0
    # for x in f1:
    #     keyWords = x.split(' ')
    #     if(num_line == 0):
    #         num_sites = keyWords[0]
    #     elif (num_line <= num_sites):
    #         connection_table.append((keyWords[0], keyWords[1]))
    #     elif(keyWords[0] == site_id):
    #         #CAUTION - Can you make multiple connections without it breaking, with the same variable?
    #         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         send_ip = int(connection_table[keyWords[1]-1][0])
    #         send_port = int(connection_table[keyWords[1]-1][1])
    #         sock.connect((send_ip, send_port)) #How do I uniquely identify each sock.connect, so that I can directly send to ex. site2 or site3...
    #         #sock.sendall(str(clock))?????
    #     num_line++;

    #time.sleep(2)
#TODO make a global listen to multiple incoming requests. sock.accept is blocking, so create your own TCP handler class

def execute_commands(site, command_file):
	#Read command file. ex - site1.txt
	with open(command_file, 'r') as f:
		for command in f.readlines():
			command = command.lower().strip()
            site.execute(command)

    # for x in f2:
    #     keyWord = x.split()
    #     if(keyWord[0] == "send"): #ex. send 2 5. site 2, $5
    #         temp_clock = q.get()
    #         max_num = max(temp_clock, clock)
    #         clock = max_num + 1
    #     elif(keyWord[0] == "snapshot"): # snapshot. Initiate snapshot by sending unique marker
    #         clock+=1
    #         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         arr = x.split(' ')
    #         ip = arr[1]
    #         send_port = int(arr[2])
    #         sock.connect((ip, send_port))
    #         sock.sendall(str(clock)) ---- 
    #         sock.close()
    #     elif(keyWord[0] == "sleep"): #sleep 5. sleep for 5 seconds, every 200ms wake up from sleep and check incoming sockets/receive all messages from them/handle
    #         clock += 1
    #     print(clock)


        #CAUTION - close all the sockets that I opeend up there
        #output line by line, every snapshot. -(snapshot_id, local state, channel state ordered by site_id)
    '''
    clock = 0
    t = threading.Thread(target=listenThread)
    t.daemon = True
    t.start()


    
    
    f = open(file, "r")
    fl = f.readlines()

    for x in fl:
        keyWord = x.split(' ')
        if(keyWord[0] == "receive"):
            temp_clock = q.get()
            max_num = max(temp_clock, clock)
            clock = max_num + 1
        elif(keyWord[0] == "call"):
            clock+=1
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            arr = x.split(' ')
            ip = arr[1]
            send_port = int(arr[2])
            sock.connect((ip, send_port))
            sock.sendall(str(clock))
            sock.close()
        else:
            clock += 1
        print(clock)
        #output line by line, every snapshot. -(snapshot_id, local state, channel state ordered by site_id)
        '''

class Message(object):
	MARKER = "M"
	def __init__(self, source_id, amount, is_marker = False):
		self.source_id = source_id
		self.amount = amount
		self.is_marker = is_marker

	def __str__(self):
		if self.is_marker:
			return str(source_id) + " " + Message.MARKER 
		else:
			return str(source_id) + " " + str(amount)

	def __repr__(self):
		return __str__(self)

	@staticmethod
	def reconstructFromString(str):
		keyWords = str.strip().split()
		source_id = int(keyWords[0])
		if keyWords[1] == Message.MARKER:
			return Message(source_id, None, is_marker = True)
		else:
			amount = int(keyWords[1])
			return Message(source_id, amount)


class Site(object):
	def __init__(self, site_id):
		self.id = site_id
		self.balance = 10
		self.addr_book = []
		self.outgoing_channels = {}
		self.incomingChannel = None

	def openIncomingChannel(self, IP, port):
		self.incomingChannel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.incomingChannel.bind( (IP, port) )
		self.incomingChannel.listen(1)

	def addOutgoingChannel(self, dest_id):
		self.outgoing_channels.put(dest_id, None)

	def openOutgoingChannels(self):
		sleep(5) #To make sure all other processes are up
		for dest_id, _ in enumerate( self.outgoing_channels ):
		self.outgoing_channels[dest_id] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.outgoing_channels[dest_id].connect(self.addr_book[dest_id - 1])

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
		

	def sendMoney(self, dest_id, amount):
		msg = Message(self.id, amount)
		outgoing_channels[dest_id].send(str(msg))

	def startSnapshot(self):

	def sleep(self, amount):
		count = (amount * 1000)/200
		i = 0
		while(i < count):
			time.sleep(0.2)
			self.checkIncomingMsgs()
			i += 1
	
if __name__ == "__main__":
	main()