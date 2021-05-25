import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 47809
UDP_BUFFER = 1024
TCP_BUFFER = 4096

UDP_SEARCHING = True

def udp_bind(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #      NEW SOCKET    INTERNET        UDP
    sock.bind((ip, port))
    return sock

def tcp_connect(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #      NEW SOCKET    INTERNET        TCP
    sock.connect((ip, port))
    return sock

def read_udp(data, addr):
    global UDP_SEARCHING
    ip, port = addr
    if data[0:2] == "UC":
        # UC found, try to search the name
        start = data.find("\xb7")
        if start > -1:
            start = start + 1
            end = data.find("\x2f")
            name = data[start:end]
            print("%s found at %s:%s" % (name,ip,port))
            UDP_SEARCHING = False
            mixer_connect(ip, port)

def mixer_connect(ip, port):
    print("Trying to connect to %s" % ip)
    tcp_sock = tcp_connect(ip, port)
    tcp_sock.send("UC\x00\x01\x1e\x00\x4a\x4d\x68\x00\x65\x00\x14\x00\x00\x00\{\" id\": \"QuerySlave \"\}")
    data = tcp_sock.recv(TCP_BUFFER)
    print(data)
    tcp_sock.close()

udp_sock = udp_bind(UDP_IP, UDP_PORT)

while UDP_SEARCHING:
  data, addr = udp_sock.recvfrom(UDP_BUFFER)
  read_udp(data, addr)
