#!/usr/bin/env python2
import socket
import time
import threading
import sys
import Queue

# argv accept input file, python asg1.py 5003 sampleP3.txt
if(len(sys.argv) != 3):
    print("Usage: python [python file] [port number] [text file]")
else:
    port = int(sys.argv[1])
    file = sys.argv[2]

TCP_IP = "0.0.0.0"
clock = 0
q = Queue.Queue()


def listenThread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, port))
    sock.listen(10)

    while True:
        stream, addr = sock.accept()
        data = stream.recv(1024)
        q.put(int(data))
        stream.close()
    
    
def process():
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
    
process()
