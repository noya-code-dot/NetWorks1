import socket
import sys

if len(sys.argv) != 3:
    print("Usage: python Client.py [serverIP] [serverPort]")
    print("Example: python Client.py 127.0.0.1 12345")
    sys.exit(1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        try:
            message = input()
        except EOFError:
            break
            
        s.sendto(message.encode('utf-8'), (HOST, PORT))

        data, server_addr = s.recvfrom(1024)
        received_string = data.decode('utf-8')
        print(f"{received_string}")

except KeyboardInterrupt:
    pass

finally:
     s.close()