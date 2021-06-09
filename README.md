# OC
Open Control is a project which tries to make an alternative to UC Surface, the official app for Presonus StudioLive RM16AI and similar mixers. The original application uses the UCnet protocol, so I am trying to understand it or at least mimic it to try to connect to my mixer.

The main purpose of this project is enable the mixer to be controlled from this alternative app. Once it is done, this app could be controlled using MIDI commands (which were not implemented on the MIDI ports of the mixer), AES70 (Open Control Aquitecture), OSC or any other relevant method.

This could allow multiple types of controllers, programming of scenes based on time or MIDI commands, remote controlling the preamps when the mixer is used as a Dante "digital snake" among other things.

# How it was made
The main project has been done by inspecting the traffic between the official Universal Control app for Windows and the mixer, but there was some data that I could'nt understand, so I just copied and pasted some byte strings to mimic the app.

Then, someone pointed me to this great documentation https://github.com/featherbear/presonus-studiolive-api/blob/documentation/PACKET.md so I made the messageEncode and messageDecode functions and no longer need to copy and paste bytes to mimic the original app.

# My understandings about UCnet
## Packets and messages
A network packet does not not always carry just one message. UC messages always start with 4 bytes: 0x55 0x43 0x00 0x01 (55 43 means UC). When my Windows app connected to my mixer, I noticed the 4 bytes were repeated on the same network packet. Then I noticed the same thing on some packets coming from the mixer, and also network packets without the four bytes.

So a single network packet can carry multiple UCnet messages, and also a UC message can be too big for a single network packet. When I noticed this, I created a buffer where all the packets are stored, from which I find and read the UC messages, and then delete them.

After the four bytes (U C 0x00 0x01) there are two bytes which represent the length in little endian. If a message is 8 bytes long, the two bytes would be 0x08 0x00. This two bytes don't include the own 4 bytes header and the 2 bytes length, so a 8 bytes long message would really be 14 bytes.

All the packets are added to the buffer. If a header is found, the length is obtained from the two next bytes. If the length is shorter than the buffer it means the full message should be in the buffer. In this case the message is sent to further processing and it is removed from the start of the buffer, leaving just the unprocessed messages. If the header length is larger than the buffer, it does nothing and keeps receiving packages until all the remaining data arrives to the buffer.

## Messages
Once connected to the mixer, each message always starts like this:
|Header|Length, little endian|Content type|Four bytes|
|:----:|:----:|:----:|:----:|
|0x55 0x43 0x00 0x01|0x08 0x00|0x4a 0x4d|0x68 0x00 0x65 0x00|

## Four Bytes
Apparently, the four bytes have two bytes that change (the first and the third) and two bytes thad stay at 0x00 (the second and the fourth). Each time the console changes the values, the app seems to interchange the order of the two that changes.
|Sender|Byte A|Byte B|Byte C|Byte D|
|:----:|:----:|:----:|:----:|:----:|
|Mixer|0x68|0x00|0x65|0x00|
|App|0x65|0x00|0x68|0x00|

## Content types
|Hexadecimal|Text|Meaning|
|:----:|:----:|:----|
|0x4a 0x4d|JM|JSON Message|
|0x42 0x4f|BO|(unknown)|
|0x43 0x4b|CK|(unknown)|
|0x46 0x44|FD|(unknown, seems to carry channel preset data)|
|0x46 0x52|FR|(unknown, used to request data from the mixer)|
|0x4b 0x41|KA|Keep alive. Sent every second to the mixer.|
|0x4d 0x53|MS|Faders positions|
|0x50 0x4c|PL|Permissions list / device list.|
|0x50 0x52|PR|(still unknown, appears when something is muted / unmuted)|
|0x50 0x53|PS|(still unknown, appears when a channel or mix name is changed)|
|0x50 0x56|PV|Parameter value.|
|0x55 0x4d|UM|UC Message. Sent when starting the connection, indicating the UDP port to receive level data.|
