import socket
import sys
def main():
    if len(sys.argv) < 3:
        print(f"NOT ENOUGH ARGUMENTS WERE GIVEN")
        return
    a_records = []
    ns_records = []
    with open(sys.argv[2], 'r') as file:
        clean_lines = [line.strip() for line in file]
    for line in clean_lines:
        
        try:
            address, ip_port_combo, record_type = line.split(',')
        except ValueError:
            print(f"Skipping malformed line: {line}")
            continue

        ip = None
        port = None
        if ':' in ip_port_combo:
            try:
                ip, port_str = ip_port_combo.split(':')
                port = int(port_str)
            except ValueError:
                print(f"Skipping line with invalid IP/port: {line}")
                continue
        else:
            ip = ip_port_combo

        record_data = {
            'address': address,
            'ip': ip,
            'port': port
        }
        print(f"Parsed record: {record_data}, Type: {record_type}")
        if record_type == 'A':
            a_records.append(record_data)
        elif record_type == 'NS':
            ns_records.append(record_data)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', int(sys.argv[1])))

    while True:

        data, addr = s.recvfrom (1024)
        print(str(data), addr)
        for record in a_records:
            if record['address'].encode() == data:
                response = f"{record['address']},{record['ip']},A"
                s.sendto(response.encode(), addr)
                break
        for record in ns_records:
            if data.endswith(record['address'].encode()):
                response = f"{record['address']},{record['ip']}:{record['port']},NS"
                s.sendto(response.encode(), addr)
                break

if __name__ == "__main__":
    main()