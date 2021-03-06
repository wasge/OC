import struct
import sys

def str2hex(s):
   return "".join("{:02x}".format(ord(c)) for c in s)

def hex2int(hex):
	hexcontent = str2hex(hex)
	# Get the two bytes little endian length
	lengtha = int(hexcontent[2:4], 16)
	lengthb = int(hexcontent[0:2], 16)
	# Convert it to decimal
	length = (lengtha * 256) + lengthb
	return length

def getLEnlength(length):
	length = struct.pack('<H', length)
	first, second = struct.unpack('>BB', length)
	return chr(first) + chr(second)

def messageEncode(fourBytes, type, content):
	# Header: \x55\x43\x00\x01 + Packet length in little endian
	header = "UC\x00\x01"
	# Packet: Type + \x68\x00\x65\x00 [+ json length in 4 bytes, little endian] + content
	if (type == "JM"): # JSON Message
		packet = type + "\x68\x00\x65\x00" # 4 unknown bytes. They sometimes change.
		# Get the JSON length in 4 bytes, little endian and add it to the packet
		# TODO This just gets the two first bytes and fakes the two last ones
		packet += getLEnlength(len(content)) + "\x00" + "\x00"
	elif (type == "UM"): # UC Message
		packet = type + "\x00\x00\x65\x00" # 4 unknown bytes. They sometimes change.
	elif (type == "FR"): # File Request
		packet = type + fourBytes # 4 unknown bytes. They sometimes change.
		packet += "\x01\x00" # This two bytes are sent before the content
	elif (type == "PV"): # Parameter Value
		packet = type + fourBytes # 4 unknown bytes. They sometimes change.
	else:
		packet = type + fourBytes
	# Add the content to the packet
	packet += content
	# Get the packet length and convert it to 2 bytes, little endian (struct "<H")
	header += getLEnlength(len(packet))
	return header + packet

count = 0
def messageDecode(content):
	global count
	header = "UC\x00\x01"
	if (content[0:4] == header):
		hexcontent = str2hex(content)
		# Get the two bytes little endian length
		lengtha = int(hexcontent[10:12], 16)
		lengthb = int(hexcontent[8:10], 16)
		# Convert it to decimal
		length = (lengtha * 256) + lengthb
		type = content[6:8]
		if (type == "JM"): # JSON content
			start = 16 # 4 first bytes + 2 little endian length bytes + 2 type bytes + 4bytes + 4 json length bytes = 16
			end = 16 + length
			print ("Received: JSON: %s" % (content[start:end]))
			#json_execute(content[start:end])
		elif (type == "PV"): # JSON content
			start = 12 # 4 first bytes + 2 little endian length bytes + 2 type bytes + 4bytes = 12
			end = 12 + length
			print ("Received: PV: %s" % (content[start:end]))
		elif (type == "PL"): # JSON content
			start = 12 # 4 first bytes + 2 little endian length bytes + 2 type bytes + 4bytes = 12
			end = 12 + length
			print ("Received: PL: %s" % (content[start:end]))
		elif (type == "CK"): # JSON content
			start = 12 # 4 first bytes + 2 little endian length bytes + 2 type bytes + 4bytes = 12
			end = 12 + length
			if (count == 1):
				'''file = open("ck_file", "w") # Write the contents of to a file for debugging
				file.write (content)
				file.close()'''
				print ("Received: CK.")
			count = 1
		elif (type == "BO"): # JSON content
			start = 12 # 4 first bytes + 2 little endian length bytes + 2 type bytes + 4bytes = 12
			end = 12 + length
			print ("Received: BO.")
		else:
			print ("Received: %s." % (type))
			start = 12 # 4 first bytes + 2 little endian length bytes + 2 type bytes + 4bytes = 12
			end = 12 + length
		return content[8:12], type, content[start:end]
	else:
		#print ("UC content NOT found: %s" % (content))
		print ("UC content NOT found.")
