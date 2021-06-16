import struct

# Values management

# Volumes, ch1-ch64
line = {}
main = {}
main["ch1"] = {}
main["ch1"]["volume"] = 0
main["ch2"] = {}
main["ch2"]["volume"] = 0
mono = {}
mono["ch1"] = {}
mono["ch1"]["volume"] = 0

for i in range(32):
	channel = (i + 1)
	line["ch" + str(channel)] = {}
	line["ch" + str(channel)]["volume"] = 0
	for j in range(16):
		aux = (j + 1)
		line["ch" + str(channel)]["aux" + str(aux)] = 0

def updateVolumes(data):
	for i in range(67):
		channel = (i + 1)
		# Get the channel volume value
		volume = data[(i*2):(i*2+2)]
		# Convert it to floating point
		volume = struct.unpack('<H', volume)
		volume = float(int(volume[0])/65535.0)
		volume = struct.pack("<f", volume)
		#print("i: %s. Channel %s: %s. Hex: %s" % (i, str(channel), volume[0], volume.encode('hex')))
		if (i < 32):
			line["ch" + str(channel)]["volume"] = volume
		if (i == 64):
			main["ch1"]["volume"] = volume
		if (i == 66):
			mono["ch1"]["volume"] = volume

def getVolume(channel):
	volume = line["ch" + channel]["volume"]
	return volume
