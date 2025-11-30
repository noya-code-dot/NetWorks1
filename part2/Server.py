import socket
import sys

def main():
    # Check if the required command-line arguments are provided (Port and file name)
    if len(sys.argv) < 3:
        print(f"NOT ENOUGH ARGUMENTS WERE GIVEN")
        return

    # Initialize lists to store the parsed A and NS records
    a_records = []
    ns_records = []

    # Open and read the zone file specified in the second argument
    with open(sys.argv[2], 'r') as file:
        # Read file, strip leading/trailing whitespace from each line
        clean_lines = [line.strip() for line in file]

    # Process each clean line from the zone file
    for line in clean_lines:
        
        try:
            # Attempt to split the line into three required fields
            address, ip_port_combo, record_type = line.split(',')
        except ValueError:
            # Skip lines that do not have exactly three comma-separated fields
            continue

        ip = None
        port = None

        # Check if the IP/port field includes a port number (separated by ':')
        if ':' in ip_port_combo:
            try:
                # Separate IP and port, and convert port string to integer
                ip, port_str = ip_port_combo.split(':')
                port = int(port_str)
            except ValueError:
                # Skip if port is not a valid integer
                continue
        else:
            # If no port is specified, the combo is just the IP
            ip = ip_port_combo

        # Structure the parsed data into a dictionary
        record_data = {
            'address': address,
            'ip': ip,
            'port': port
        }

        # Classify the record and add it to the corresponding list
        if record_type == 'A':
            a_records.append(record_data)
        elif record_type == 'NS':
            ns_records.append(record_data)

    # Initialize the UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the specified port (first argument)
    s.bind(('127.0.0.1', int(sys.argv[1])))

    # Main server loop to continuously listen for queries
    while True:
        found = False
        # Wait for data from a client (blocking call)
        data, addr = s.recvfrom (1024)
        #print(str(data), addr)

        # 1. Search for an exact match (A Record)
        for record in a_records:
            # Compare the queried domain (in bytes) with the A record address
            if record['address'].encode() == data:
                # Format the A record response: domain,ip,A
                response = f"{record['address']},{record['ip']},A"
                s.sendto(response.encode(), addr)
                found = True
                break
        
        # 2. If no exact A record found, search for a matching NS Record
        if not found:
            # Loop through all configured NS (Name Server) records
            for record in ns_records:
                # Check if the queried domain ends with the NS address (suffix match)
                if data.endswith(record['address'].encode()):
                    # Format the NS response: domain,ip:port,NS
                    response = f"{record['address']},{record['ip']}:{record['port']},NS"
                    s.sendto(response.encode(), addr)
                    found = True
                    break

        # 3. If no match (A or NS) was found
        if(found is not True):
            # Send the "non-existent domain" error message
            s.sendto(b"non-existent domain", addr)

if __name__ == "__main__":
    main()