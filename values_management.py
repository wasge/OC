# Values management

# Volumes, ch1-ch64
line = {}

for i in range(32):
	channel = (i + 1)
	line["ch" + str(channel)] = {}
	line["ch" + str(channel)]["main"] = 0

def updateVolumes(data):
	for i in range(32):
		channel = (i + 1)
		line["ch" + str(channel)]["main"] = data[(i*2):(i*2+2)]

def getVolume(channel):
	volume = line["ch" + channel]["main"]
	return volume
