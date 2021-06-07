# OC
Open Control is a project which tries to make an alternative to UC Surface, the official app for Presonus StudioLive RM16AI and similar mixers. The original application uses the UCnet protocol, so I am trying to understand it or at least mimic it to try to connect to my mixer.

The main purpose of this project is enable the mixer to be controlled from this alternative app. Once it is done, this app could be controlled using MIDI commands (which were not implemented on the MIDI ports of the mixer), AES70 (Open Control Aquitecture), OSC or any other relevant method.

This could allow multiple types of controllers, programming of scenes based on time or MIDI commands, remote controlling the preamps when the mixer is used as a Dante "digital snake" among other things.

# How it was made
The main project has been done by inspecting the traffic between the official Universal Control app for Windows and the mixer, but there was some data that I could'nt understand, so I just copied and pasted some byte strings to mimic the app.

Then, someone pointed me to this great documentation https://github.com/featherbear/presonus-studiolive-api/blob/documentation/PACKET.md so I made the package_encode function and no longer need to copy andn paste bytes to mimic the original app.
