# nad_receiver
Simple python API to connect to NAD receivers through the RS232 interface.

Note that this is only tested with the NAD T748v2. Commands are implemented based on the T748v2. Those commands should work with more NAD receivers.
The supported commands can easily be extended for receivers which support more commands.

For more information see the official documentation at http://nadelectronics.com/software 

Usage:
```
receiver = NADReceiver(serial_port)  # e.g. /dev/ttyUSB0

receiver.main_volume('+')  #  will increase volume with 1 and return new value
receiver.main_volume('-')  #  will decrease volume with 1 and return new value
receiver.main_volume('=', '-40')  # specify dB, will return new value
print(receiver.main_volume('?'))  # will return current value
```

supported commands with supported operators

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

# D7050
The D7050 class supports the NAD D 7050 amplifier and communicates via tcp/ip.

Usage:
```
D7050 = D7050(host_ip)

D7050.power_on()
D7050.status()  # Returns a dictionary with keys 'volume', 'power', 'muted' and 'source'.
D7050.set_volume(150)
sources = D7050.available_sources()
D7050.select_source('Optical 1')
D7050.mute()
D7050.unmute()
D7050.power_off()
```
