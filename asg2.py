#!/usr/bin/env python2
import socket
import time
import threading
import sys
import Queue

# argv accept input file, python asg2.py 1 setup.txt site1.txt
if(len(sys.argv) != 3):
    print("Usage: python [site_id] [setup_file] [command_file]")
else:
    site_id = int(sys.argv[1])
    setup_file = sys.argv[2]
    command_file = sys.argv[3]


TCP_IP = "0.0.0.0"
connection_table = []
q = Queue.Queue()
snapshot_counter = 0

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

def process():
#Read setup file. ex - setup.txt     
    #time.sleep(5)
    setupFileResult = open(setup_file, "r")
    fl = setupFileResult.readlines()
    num_line = 0
    num_sites = 0
    for x in f1:
        keyWords = x.split(' ')
        if(num_line == 0):
            num_sites = keyWords[0]
        elif (num_line <= num_sites):
            connection_table.append((keyWords[0], keyWords[1]))
        elif(keyWords[0] == site_id):
            #CAUTION - Can you make multiple connections without it breaking, with the same variable?
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_ip = int(connection_table[keyWords[1]-1][0])
            send_port = int(connection_table[keyWords[1]-1][1])
            sock.connect((send_ip, send_port)) #How do I uniquely identify each sock.connect, so that I can directly send to ex. site2 or site3...
            #sock.sendall(str(clock))?????
        num_line++;

    time.sleep(2)
#TODO make a global listen to multiple incoming requests. sock.accept is blocking, so create your own TCP handler class

#Read command file. ex - site1.txt
    commandFileResult = open(command_file, "r")
    f2 = commandFileResult.readLines()
    
    for x in f2:
        keyWord = x.split(' ')
        if(keyWord[0] == "send"): #ex. send 2 5. site 2, $5
            temp_clock = q.get()
            max_num = max(temp_clock, clock)
            clock = max_num + 1
        elif(keyWord[0] == "snapshot"): # snapshot. Initiate snapshot by sending unique marker
            clock+=1
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            arr = x.split(' ')
            ip = arr[1]
            send_port = int(arr[2])
            sock.connect((ip, send_port))
            sock.sendall(str(clock)) ---- 
            sock.close()
        elif(keyWord[0] == "sleep"): #sleep 5. sleep for 5 seconds, every 200ms wake up from sleep and check incoming sockets/receive all messages from them/handle
            clock += 1
        print(clock)


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
    
process()
