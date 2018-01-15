# nad_receiver
Simple python API to connect to NAD receivers through the RS232 interface, Telnet interface or the TCP/IP interface.
For the RS232 interface use the NADReceiver class
For the Telnet interface use the NADReceiverTelnet class
For the TCP/IP interface use the D7050 class

Note that the RS232 interface is only tested with the NAD T748v2. Commands are implemented based on the T748v2. Those commands should work with more NAD receivers.
The Telnet interface is only tested with the NAD T787. The Telnet interface share documentation with the RS232 interface and supports the same commands
The supported commands can easily be extended for receivers which support more commands.

For more information see the official documentation at http://nadelectronics.com/software 

Usage:
```
receiver = NADReceiver(serial_port)  # e.g. /dev/ttyUSB0

receiver.main_volume('+')  #  will increase volume with 1 and return new value
receiver.main_volume('-')  #  will decrease volume with 1 and return new value
receiver.main_volume('=', '-40')  # specify dB, will return new value
print(receiver.main_volume('?'))  # will return current value

D7050 = NADReceiverTCP(host_ip)  # The IP address of your amplifier in the network.

D7050.power_on()
D7050.available_sources()  # Returns a list of available sources in human readable format.
D7050.status()  # Returns a dictionary with keys 'volume', 'power', 'muted' and 'source'.
D7050.set_volume(150)  # Set volume level. min = 0 = -90dB, max = 200 = +10dB.
sources = D7050.available_sources()
D7050.select_source('Optical 1')
D7050.mute()
D7050.unmute()
D7050.power_off()

receiver = NADReceiverTelnet(my_nad.local)

receiver.main_volume('+')  #  will increase volume with 1 and return new value
receiver.main_volume('-')  #  will decrease volume with 1 and return new value
receiver.main_volume('=', '-40')  # specify dB, will return new value
print(receiver.main_volume('?'))  # will return current value
```

supported commands with supported operators for the RS232 interface

* main_volume [ +, -, =, ? ]
* main_mute [ +, -, =, ? ]
* main_power [ +, -, =, ? ]
* main_listeningmode [ +, - ]
* main_version [ ? ]
* main_dimmer [ +, -, =, ? ]
* main_ir [ = ]
* main_source [ +, -, =, ? ]
* main_sleep [ +, - ]
* tuner_fm_preset [ +, -, =, ? ]
* tuner_band [ +, -, =, ? ]
* tuner_am_frequency [ +, - ]
* tuner_am_preset [ +, -, =, ? ]
* tuner_fm_mute [ +, -, =, ? ]
* tuner_fm_frequency [ +, - ]


