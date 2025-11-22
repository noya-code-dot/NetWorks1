import socket
import sys
import time

cache = {}

if len(sys.argv) != 5:
    print("Usage: python resolver.py [myPort] [parentIP] [parentPort] [x]")
    sys.exit(1)

MY_PORT = int(sys.argv[1])
PARENT_IP = sys.argv[2]
PARENT_PORT = int(sys.argv[3])
x = int(sys.argv[4])

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', MY_PORT))

while True:
    data, client_addr = s.recvfrom(1024)
    received_string = data.decode('utf-8').strip()
    
    domain = received_string  
    isThere = False

    if domain in cache:
        response, expiration = cache[domain]
        if time.time() < expiration: 
            isThere = True
        else:
            del cache[domain]

    if isThere:
        s.sendto(response.encode(), client_addr)
    else:
        s.sendto(domain.encode(), (PARENT_IP, PARENT_PORT))
        
        data2, server_addr = s.recvfrom(1024)
        received_string2 = data2.decode('utf-8').strip()  
        response = received_string2
        
        cache[domain] = (response, time.time() + x)
        
        s.sendto(response.encode(), client_addr)
