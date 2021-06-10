import json
import socket
import sys
import threading
import time
from packet_encode_decode import messageEncode, messageDecode, getLEnlength, hex2int, str2hex
from values_management import getVolume, updateVolumes

UDP_IP = "0.0.0.0"
UDP_PORT = 47809
UDP_BUFFER = 1024
TCP_BUFFER = 4096

fourBytesA = "\x68"
fourBytesC = "\x65"

UDP_SEARCHING = True
MIXER_CONNECTED = True
packet_buffer = ""

debugMessages = False

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

def fourBytesUpdater(fourBytes):
	global fourBytesA, fourBytesC
	# Just set the two bytes when received
	fourBytesA = fourBytes[0:1]
	fourBytesC = fourBytes[2:3]
	#print str2hex(fourBytesA + "\x00" + fourBytesC + "\x00")

def fourBytesGenerator():
	# Interchange the two non-zero fourBytes
	string = fourBytesC + "\x00" + fourBytesA + "\x00"
	return string

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
				fourBytes, type, content = messageDecode(message) # Process the message
				fourBytesUpdater(fourBytes)
				analyzeMessage(type, content)
				packet_buffer = packet_buffer[messagePos+6+length:] # Remove this chunk from the buffer
				searchPos = 0
			messagePos = 0
		else:
			searching = False

def analyzeMessage(type, content):
	global tcp_sock
	fourBytes = fourBytesGenerator()
	if (type == "JM"): # JSON message
		content = json.loads(content)
		for id in content:
			if (content["id"] == "UpdateSlave"): # Mixer answered the first call.
				messagea = messageEncode(fourBytes, "UM", "\xca\xc5") # UDP port on the computer to receive UDP data from the mixer
				messageb = messageEncode(fourBytes, "JM", "{\"id\": \"Subscribe\", \"clientName\": \"Universal Control AI\", \"clientInternalName\": \"ucapp\", \"clientType\": \"PC\", \"clientDescription\": \"Open Control\", \"clientIdentifier\": \"WASGE-OC\", \"clientOptions\": \"perm users levl redu\", \"clientEncoding\": 23117}")
				print(">>> UM + Subscribe")
				tcp_sock.send(messagea + messageb)
			elif (content["id"] == "SubscriptionReply"): # Ask for the presets list.
				message = messageEncode(fourBytes, "FR", "Listpresets/channel\x00\x00")
				tcp_sock.send(message)
				print(">>> Listpresets/channel")
			elif (content["id"] == "SubscriptionLost"): # Lost Subscription, exit the program
				sys.exit()
	elif (type == "PL"):
		message = messageEncode(fourBytes, "PV", "main/ch1/volume\x00\x00\x00\xb9\x65\xc5\x3f") # MOVE THE MAIN FADER! FINALLY!!!
		tcp_sock.send(message)
		print(">>> PV")
		#tcp_sock.send(message)
		#print(">>> PV main/ch/volume")
	elif (type == "MS"):
		updateVolumes(content[8:])
		if debugMessages:
			print("MS content: %s" % (str2hex(content[8:])))


def mixer_connect(ip, port):
	global tcp_sock
	print("Trying to connect to %s:%s" % (ip, port))
	tcp_sock = tcp_connect(ip, port)
	fourBytes = fourBytesGenerator()
	packet = messageEncode(fourBytes, "JM", "{\"id\": \"QuerySlave\"}")
	print(">>> QuerySlave")
	tcp_sock.send(packet)
	# Create the keepAlive Trhead and start it
	keepThread = threading.Thread(target=keepAlive)
	keepThread.daemon = True
	keepThread.start()
	#packet = messageEncode("FR", "Listpresets/channel\x00\x00")
	#packet = messageEncode("PV", "main/ch1/volume\x00\x00\x00\x27\x57\x10\x3f")
	#tcp_sock.send(packet)
	while MIXER_CONNECTED == True:
		data = tcp_sock.recv(TCP_BUFFER)
		message_search(data)
	print ("Exit")
	tcp_sock.close()

def keepAlive(): # Send a keepAlive message every one second
	global lastKeepAlive, tcp_sock
	while True:
		curTime = time.time()
		if curTime - lastKeepAlive > 1.0:
			fourBytes = fourBytesGenerator()
			message = messageEncode(fourBytes, "KA", "")
			tcp_sock.send(message)
			if debugMessages:
				print(">>> KeepAlive. fourBytes: %s" % (str2hex(fourBytes)))
			lastKeepAlive = curTime
			time.sleep(1)

if __name__ == "__main__":
	udp_sock = udp_bind(UDP_IP, UDP_PORT)
	
	while UDP_SEARCHING:
		data, addr = udp_sock.recvfrom(UDP_BUFFER)
		read_udp(data, addr)
