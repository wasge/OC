# OC
Open Control is a project which tries to make an alternative to UC Surface, the official app for Presonus StudioLive RM16AI and similar mixers. The original application uses the UCnet protocol, so I am trying to understand it or at least mimic it to try to connect to my mixer.

The main purpose of this project is enable the mixer to be controlled from this alternative app. Once it is done, this app could be controlled using MIDI commands (which were not implemented on the MIDI ports of the mixer), AES70 (Open Control Aquitecture), OSC or any other relevant method.

This could allow multiple types of controllers, programming of scenes based on time or MIDI commands, remote controlling the preamps when the mixer is used as a Dante "digital snake" among other things.

# How it was made
The main project has been done by inspecting the traffic between the official Universal Control app for Windows and the mixer, but there was some data that I could'nt understand, so I just copied and pasted some byte strings to mimic the app.

Then, someone pointed me to this great documentation https://github.com/featherbear/presonus-studiolive-api/blob/documentation/PACKET.md so I made the messageEncode and messageDecode functions and no longer need to copy and paste bytes to mimic the original app.

# My understandings about UCnet
## Packets and messages
A network packet does not not always carry just one message. UC messages always start with 4 bytes: 0x55 0x43 0x00 0x01 (55 43 means UC). When my Windows app connected to my mixer, I noticed the 4 bytes were repeated on the same network packet. Then I noticed the same thing on some packets coming from the mixer, and also network packets without the four bytes. So I created a buffer, from which I read the messages.

After the four bytes (U C 0x00 0x01) there are two bytes which represent the length in little endian. If a message is 8 bytes long, the two bytes would be 0x08 0x00. This two bytes don't include the own 4 bytes header and the 2 bytes length, so a 8 bytes long message would really be 14 bytes.

All the packets are added to the buffer. If a header is found, the length is obtained from the two next bytes. If the length is shorter than the buffer, the message is sent to further processing and it is removed from the start of the buffer, leaving just the unprocessed messages. If the header length is shorter than the buffer, it does nothing and keeps receiving packages until all the remaining data arrives to the buffer.
