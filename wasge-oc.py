import socket
import threading
from packet_encode_decode import messageEncode, messageDecode, getLEnlength, hex2int

UDP_IP = "0.0.0.0"
UDP_PORT = 47809
UDP_BUFFER = 1024
TCP_BUFFER = 4096

UDP_SEARCHING = True
MIXER_CONNECTED = True
packet_buffer = ""

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
        print("Data received from a mixer")
        # UC found, try to search the name
        start = data.find("\xb7")
        if start > -1:
            start = start + 1
            end = data.find("\x2f")
            name = data[start:end]
            print("%s found at %s:%s" % (name,ip,port))
            UDP_SEARCHING = False
            udp_sock.close()
            mixer_connect(ip, port)

def message_search(packet): # There are multiple messages per packet
	global packet_buffer # And messages on multiple packets, so we need a buffer
	searching = True
	searchPos = 0
	packet_buffer += packet # Add the new packet to the buffer
	while (searching == True):
		position = packet_buffer.find("\x55\x43\x00\x01", searchPos) # Search for the header
		if (position > -1):
			messagePos = position # Position of the message
			length = hex2int(packet_buffer[messagePos+4:messagePos+6]) # Length of the message
			if (length > len(packet_buffer)): # Not enough data, keep searching
				break
			else: # Enough data, message complete
				message = packet_buffer[messagePos:messagePos+6+length]
				messageDecode(message) # Process the message
				packet_buffer = packet_buffer[messagePos+6+length:] # Remove this chunk from the buffer
				searchPos = 0
			messagePos = 0
		else:
			searching = False

def mixer_connect(ip, port):
    print("Trying to connect to %s:%s" % (ip, port))
    tcp_sock = tcp_connect(ip, port)
    packet = messageEncode("JM", "{\"id\": \"QuerySlave\"}")
    print(">>>QuerySlave")
    tcp_sock.send(packet)
    data = tcp_sock.recv(TCP_BUFFER)
    messageDecode(data)
    packeta = messageEncode("UM", "\xca\xc5") # UDP port on the computer to receive UDP data from the mixer
    packetb = messageEncode("JM", "{\"id\": \"Subscribe\", \"clientName\": \"Universal Control AI\", \"clientInternalName\": \"ucapp\", \"clientType\": \"PC\", \"clientDescription\": \"WASGE OC\", \"clientIdentifier\": \"WASGE-OC\", \"clientOptions\": \"perm users levl redu\", \"clientEncoding\": 23117}")
    print(">>>UM")
    print(">>>Subscribe")
    tcp_sock.send(packeta + packetb)
    #data = tcp_sock.recv(TCP_BUFFER)
    #messageDecode(data)
    #packet = messageEncode("FR", "Listpresets/channel\x00\x00")
    #packet = messageEncode("PV", "main/ch1/volume\x00\x00\x00\x27\x57\x10\x3f")
    #tcp_sock.send(packet)
    while MIXER_CONNECTED == True:
        data = tcp_sock.recv(TCP_BUFFER)
        message_search(data)
    print ("Exit")
    tcp_sock.close()

if __name__ == "__main__":
	udp_sock = udp_bind(UDP_IP, UDP_PORT)
	
	while UDP_SEARCHING:
		data, addr = udp_sock.recvfrom(UDP_BUFFER)
		read_udp(data, addr)
