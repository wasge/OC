import json
import select
import socket
import struct
import sys
import threading
import time
from packet_encode_decode import messageEncode, messageDecode, hex2int, str2hex
from values_management import getVolume, updateVolumes
from oscInterface import analyzeOSC

UDP_IP = "0.0.0.0"
UDP_PORT = 47809
UDP_BUFFER = 1024

TCP_BUFFER = 4096
TCP_IP = "0.0.0.0"
TCP_PORT = 0

OSC_ENABLE = False
OSC_IP = "0.0.0.0"
OSC_PORT = 8088

fourBytesA = b"\x68"
fourBytesC = b"\x65"

UDP_SEARCHING = True
MIXER_CONNECTED = True
packet_buffer = b""

debugMessages = True

lastKeepAlive = time.time()

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
    if data[0:2] == b"UC":
        print("Data received from a mixer")
        # UC found, try to search the name
        start = data.find(b"Studio")
        if start > -1:
            end = data.find(b"\x00", start)
            name = data[start:end]
            print("%s found at %s:%s" % (name.decode(),ip,port))
            UDP_SEARCHING = False
            udp_sock.close()
            mixer_connect(ip, port)

def fourBytesUpdater(fourBytes):
	global fourBytesA, fourBytesC
	# Just set the two bytes when received
	fourBytesA = fourBytes[0:1]
	fourBytesC = fourBytes[2:3]

def fourBytesGenerator():
	# Interchange the two non-zero fourBytes
	string = fourBytesC + b"\x00" + fourBytesA + b"\x00"
	return string

def message_search(packet): # There might be multiple UCnet messages per packet
	global packet_buffer # And messages on multiple packets, so we need a buffer
	searching = True
	searchPos = 0
	packet_buffer += packet # Add the new packet to the buffer
	while (searching == True):
		position = packet_buffer.find(b"\x55\x43\x00\x01", searchPos) # Search for the header
		if (position > -1):
			messagePos = position # Position of the message
			length = hex2int(packet_buffer[messagePos+4:messagePos+6]) # Length of the message
			if (length > len(packet_buffer)): # Not enough data, keep searching
				break
			else: # Enough data, message complete
				message = packet_buffer[messagePos:messagePos+6+length]
				fourBytes, type, content = messageDecode(message) # Process the message
				fourBytesUpdater(fourBytes)
				analyzeMessage(type, content)
				packet_buffer = packet_buffer[messagePos+6+length:] # Remove this chunk from the buffer
				searchPos = 0
			messagePos = 0
		else:
			searching = False

def OSC_search(data): # There might be multiple OSC messages (a bundle) in a single packet
	if (data[0:8] == "#bundle\x00"):
		osc_buffer = data[16:] # Remove the first 8 bytes: #buffer\x00 + the next 8 bytes: the OSC timetag
		while (len(osc_buffer) > 4):
			length = osc_buffer[0:4] # OSC message length, 32 bit int
			length = struct.unpack('>i', length)[0]
			length = length + 4 # Add the length of 4 bytes indicating the length
			data = osc_buffer[4:length] # Remove the length from the data
			command, value = analyzeOSC(data)
			doThing(command, value)
			osc_buffer = osc_buffer[length:] # Remove this chunk from the buffer
	else:
		command, value = analyzeOSC(data)
		doThing(command, value)

def analyzeMessage(type, content):
	global tcp_sock
	if debugMessages:
		print(f"Main: analyzeMessage: type: {type}")
	fourBytes = fourBytesGenerator()
	if (type == b"JM"): # JSON message
		content = json.loads(content)
		for id in content:
			if (content["id"] == "UpdateSlave"): # Mixer answered the first call.
				messagea = messageEncode(fourBytes, "UM", b"\xca\xc5") # UDP port on the computer to receive UDP data from the mixer
				messageb = messageEncode(fourBytes, "JM", "{\"id\": \"Subscribe\", \"clientName\": \"Universal Control AI\", \"clientInternalName\": \"ucapp\", \"clientType\": \"PC\", \"clientDescription\": \"Open Control\", \"clientIdentifier\": \"WASGE-OC\", \"clientOptions\": \"perm users levl redu\", \"clientEncoding\": 23117}".encode())
				print(">>> UM + Subscribe")
				tcp_sock.send(messagea + messageb)
			elif (content["id"] == "SubscriptionReply"): # Ask for the presets list.
				message = messageEncode(fourBytes, "FR", "Listpresets/channel\x00\x00".encode())
				print(">>> Listpresets/channel")
				tcp_sock.send(message)
			elif (content["id"] == "SubscriptionLost"): # Lost Subscription, exit the program
				sys.exit()
	#elif (type == "PL"):
		#message = messageEncode(fourBytes, "PV", "main/ch1/volume\x00\x00\x00\xb9\x65\xc5\x3f") # MOVE THE MAIN FADER! FINALLY!!!
		#message = messageEncode(fourBytes, "PV", "main/ch1/volume\x00\x00\x00\x03\x25\x3c\x3f") # MOVE THE MAIN FADER! FINALLY!!!
		#tcp_sock.send(message)
		#print(">>> PV")
		#tcp_sock.send(message)
		#print(">>> PV main/ch/volume")
	elif (type == b"MS"):
		updateVolumes(content[8:])
		if debugMessages:
			print("MS content: %s" % (str2hex(content[8:])))

def doThing(command, value):
	global tcp_sock
	#fullvalue = "main/ch1/volume\x00\x00\x00\x03\x25\x3c\x3f"
	fullvalue = (command[1:] + "\x00\x00\x00" + value) # Remove the first "/" with command[1:]
	print (">>> PV: Command: %s Value:%s" % (command[1:], str2hex(value)))
	fourBytes = fourBytesGenerator()
	message = messageEncode(fourBytes, "PV", fullvalue)
	tcp_sock.send(message)

def mixer_connect(ip, port):
	global tcp_sock, osc_sock, TCP_IP, TCP_PORT
	TCP_IP = ip
	TCP_PORT = port
	print("Trying to connect to %s:%s" % (TCP_IP, TCP_PORT))
	tcp_sock = tcp_connect(TCP_IP, TCP_PORT) # Start the connection to the mixer
	osc_sock = udp_bind(OSC_IP, OSC_PORT) # Start the OSC binding
	fourBytes = fourBytesGenerator()
	packet = messageEncode(fourBytes, "JM", "{\"id\": \"QuerySlave\"}".encode())
	print(">>> QuerySlave")
	tcp_sock.send(packet)
	keepThread = threading.Thread(target=keepAlive) #Create the keepAlive Trhead and start it
	keepThread.daemon = True
	keepThread.start()
	empty = []
	while MIXER_CONNECTED == True:
		readable, writable, exceptional = select.select((tcp_sock, osc_sock), empty, empty) # Select data from both sockets
		for s in readable:
			data, address = s.recvfrom(TCP_BUFFER)
			if (address[0] == 0): # It is the TCP connection
				message_search(data) # Search for UCnet messages on the packet
			else: # It is the OSC bind
				OSC_search(data) # Search for OSC messages on the packet
	print ("Exit")
	tcp_sock.close()

def keepAlive(): # Send a keepAlive message every one second
	global lastKeepAlive, tcp_sock
	while True:
		curTime = time.time()
		if curTime - lastKeepAlive > 1.0:
			fourBytes = fourBytesGenerator()
			message = messageEncode(fourBytes, "KA", "")
			tcp_sock.send(message.encode())
			if debugMessages:
				print(">>> KeepAlive. fourBytes: %s" % (str2hex(fourBytes)))
			lastKeepAlive = curTime
			time.sleep(1)

if __name__ == "__main__":
	udp_sock = udp_bind(UDP_IP, UDP_PORT)
	
	while UDP_SEARCHING:
		data, addr = udp_sock.recvfrom(UDP_BUFFER)
		read_udp(data, addr)
