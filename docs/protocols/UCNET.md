# My understandings about UCNET
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
|0x42 0x4f|BO|(unknown)|
|0x43 0x4b|CK|(unknown)|
|0x46 0x44|FD|(unknown, seems to carry channel preset data)|
|0x46 0x52|FR|(unknown, used to request data from the mixer)|
|0x4a 0x4d|JM|JSON Message|
|0x4b 0x41|KA|Keep alive. Sent every second to the mixer.|
|0x4d 0x53|MS|Faders positions. After the four bytes, each two bytes in little endian (from 0 to 65535) represent the fader position from channel 1 to 64. The next is the main fader. The next is unknown. The next is the mono fader.|
|0x4a 0x4d|PC|(unknown, seems to change when changing the colour of a channel)|
|0x50 0x4c|PL|Permissions list / device list.|
|0x50 0x52|PR|(unknown, appears when something is muted / unmuted)|
|0x50 0x53|PS|(unknown, appears when a channel or mix name is changed)|
|0x50 0x56|PV|Parameter value.|
|0x55 0x4d|UM|UDP port opened on the app to receive channels levels data. Example: 0xCA 0xC5 in little endian means C5CA = port 50634.|

## PV contents
The mixer is organized like an analog mixer, not like a digital one. The aux sends are part of each channel.
|Parameter|Name|Value|Comments|
|:---|:---|:---|:---|
|Main mix > volume|main/ch1/volume|0 (`0x00 0x00 0x00 0x00`) to 1 (`0x00 0x00 0x80 0x3F`) in little endian 32 bits floating point|Main mix, although being a stereo channel, is referred to just ch1|
|Mono out > Mute on/off|mono/ch1/mute|`0x00 0x00 0x80 0x3F` = mute on (no sound passing) / `0x00 0x00 0x00 0x00` = mute off (sound passes through)|If the main mix is set to LCR (instead of LR + mono) it works exactly the same, it is still called mono/ch1|
|Channel 1 > Preamp gain|line/ch1/preampgain|||
|Channel 1 > High pass filter|line/ch1/filter/hpf|||
|Channel 1 > Phantom power on/off|line/ch1/48v|||
|Channel 1 > Inverse polarity on/off|line/ch1/polarity|||
|Channel 1 > Route to Main mix on/off|line/ch1/lr|||
|Channel 1 > Route to Mono mix on/off|line/ch1/mono|||
|Channel 1 > Mute on/off|line/ch1/mute|||
|Channel 1 > Solo on/off|line/ch1/solo|||
|Channel 1 > Pan|line/ch1/pan|||
|Channel 1 > Gate on/off|line/ch1/gate/on|||
|Channel 1 > Compressor on/off|line/ch1/comp/on|||
|Channel 1 > Equalizer on/off|line/ch1/eq/eqallon|||
|Channel 1 > Limiter on/off|line/ch1/limit/limiteron|||
|Channel 1 > Send to FX A|line/ch1/FXA|||
|Channel 1 > Send to Aux 1 > level|line/ch1/aux1|||
|Channel 1 > Send to Aux 1+2 > pan|line/ch1/aux12_pan||Aux 12 (an even number) is aux 1+2, it cannot be aux 12, as it would mean it also exist aux 11, and both of them would be mono auxes so they can't have pan.|
|Channel 1 > Send to Aux 15+16 > pan|line/ch1/aux1516_pan|||
|Aux Mix 1 > Main output|aux/ch1/volume|0 to 1 in little endian 32 bits floating point||
|Aux Mix 1 > Stereo link with Aux Mix 2|aux/ch12/link||It is Aux 1+2. It cannot be aux 12, as it would be aux 11 + 12, not just 12 alone|
