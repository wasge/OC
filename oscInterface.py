def analyzeOSC(data):
	start = data.find(",")
	if start > -1:
		addressStart = data.find("/")
		addressEnd = data.find("\x00", addressStart)
		address = data[addressStart:addressEnd]
		value = data[(start + 4):]
		value = value[3:4] + value[2:3] + value[1:2] + value[0:1] # Reverse the 4 bytes
		return address, value
	else:
		return False, False
