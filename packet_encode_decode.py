import struct

def packet_encode(type, content):
	# Header: \x55\x43\x00\x01 + Packet length in little endian
	header = "UC\x00\x01"
	# Packet: Type + \x68\x00\x65\x00 [+ json length in 4 bytes, little endian] + content
	if (type == "JM"): # JSON Message
		packet = type + "\x68\x00\x65\x00"
		# Get the JSON length in 4 bytes, little endian and add it to the packet
		# TODO This just gets the two first bytes and fakes the two last ones
		jsonlenlength = struct.pack('<H', len(content))
		first, second = struct.unpack('>BB', jsonlenlength)
		packet +=  chr(first) + chr(second) + "\x00" + "\x00"
	elif (type == "UM"): # UC Message
		packet = type + "\x00\x00\x65\x00"
	elif (type == "FR"): # File Request
		packet = type + "\x6b\x00\x65\x00"
		packet += "\x01\x00"
	else:
		packet = type + "\x68\x00\x65\x00"		
	# Add the content to the packet
	packet += content
	# Get the packet length and convert it to 2 bytes, little endian (struct "<H")
	lenlength = struct.pack('<H', len(packet))
	first, second = struct.unpack('>BB', lenlength)
	header += chr(first) + chr(second)
	return header + packet

# result = packet_encode("JM", "{\"id\": \"QuerySlave\"}")
# result = packet_encode("UM", "\xca\xc5")
# Print reult in hex
# print(":".join("{:02x}".format(ord(c)) for c in result))
