# OC
Open Control is a **Python 2** project which I'm slowly translating to Python 3 witch tries to make an alternative to UC Surface, the official app for Presonus StudioLive RM16AI and similar mixers. The original application uses the UCnet protocol, so I am trying to understand it or at least mimic it to try to connect to my mixer.

The main purpose of this project is enable the mixer to be controlled from this alternative app. Once it is done, this app could be controlled using MIDI commands (which were not implemented on the MIDI ports of the mixer), AES70 (Open Control Aquitecture), OSC or any other relevant method.

This could allow multiple types of controllers, programming of scenes based on time or MIDI commands, remote controlling the preamps when the mixer is used as a Dante "digital snake" among other things.

## Status
* It is able to connect to the mixer. It appears on the official applications as one more device.
* It is able to receive and store faders positions once any fader is moved, **not at the start** of the application.
* It is able to receive OSC messages.
* **It is able to move faders when receiving OSC messages.**

This application needs Python 2 (yes, I know it's discontinued, but I didn't knew it wen I started the project).

It also needs to open the UDP port 47809 to listen for discovery messages from available mixers. The app "UC Surface" and the Windows service "Presonus Hardware Access Service" needs to be closed, as they are using (and thus blocking) the port.

## How it was made
The main project has been done by inspecting the traffic between the official Universal Control app for Windows and the mixer, but there was some data that I could'nt understand, so I just copied and pasted some byte strings to mimic the app.

Then, someone pointed me to this great documentation https://github.com/featherbear/presonus-studiolive-api/blob/documentation/PACKET.md so I made the messageEncode and messageDecode functions and no longer need to copy and paste bytes to mimic the original app.

## Open Sound Control
The project has a very basic working OSC implementation, only capable of receiving fader information and sending it to the mixer. It does **not** sends back to the OSC client the movement of the faders made from other UC Surface apps or CS18 controllers.

It accepts OSC messages, without main URL address, and with addresses `/main/ch1/volume` or `/line/ch1/volume` to `/line/ch32/volume` and receives data from 0 (minimum value) to 1 (maximum value) in little endian 32 bits floating point.

## Files
### wasge-oc.py
It is the main program, basically the place where I'm doing all the tests. It has the config at the start of the file.

It listens for dicovery broadcast UDP packages sent from the mixer. Then, when a mixer is detected it automatically starts the TCP connection and starts the session.
### packet_encode_decode.py
Originally it had two functions, packet_encode and packet_decode. Since I discovered that the important things are the messages inside the packets, I renamed it to messageEncode and messageDecode. There are also some small functions to convert hexadecimal values to string or get the integer of a little endian value.
### values_management.py
This file creates the variables for the faders positions, updates it when requested by wasge-oc.py and returns the position of a given fader when requested. It also converts the 16 bit little endian fader position (0 - 65535) to floating point (0 - 1) to match the rest of the values sent to the mixer.

# Protocols used by OC
When I created this application, I targeted just my Presonus RM16AI mixer, but I'm trying to be adaptable to more devices.
## Presonus StudioLive mixers
[My understandings about UCNET](docs/protocols/UCNET.md)
