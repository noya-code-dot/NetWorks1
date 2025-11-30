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
    print(f"{received_string}")

    domain = received_string  
    isThere = False
    response = None

    if domain in cache:
        cached_resp, expiration = cache[domain]
        if time.time() < expiration: 
            s.sendto(cached_resp.encode(), client_addr)
            continue 
        else:
            del cache[domain]

    if not isThere:
        s.sendto(domain.encode(), (PARENT_IP, PARENT_PORT))
        
        data2, server_addr = s.recvfrom(1024)
        received_string2 = data2.decode('utf-8').strip()  
        response = received_string2
        
        cache[domain] = (response, time.time() + x)

    while response.endswith("NS"):
        #print(f"{received_string2}")

        parts = response.split(',')
        ns_ip, ns_port = parts[1].split(':')
        ns_port = int(ns_port)
        s.sendto(domain.encode(), ('127.0.0.1', ns_port))
        data2, server_addr = s.recvfrom(1024)
        received_string2 = data2.decode('utf-8').strip() 
        response = received_string2
        cache[domain] = (response, time.time() + x)

    #print(f"{response}")

    if response == "non-existent domain":
        cache[domain] = (response, time.time() + x)
        s.sendto(response.encode(), client_addr)

    elif response.endswith(",A"):
        parts = response.split(',')
        ip_only = parts[1]

        cache[domain] = (ip_only, time.time() + x)
        s.sendto(ip_only.encode(), client_addr)
