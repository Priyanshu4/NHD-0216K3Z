# NHD-0216K3Z
Python module for controlling the NHD-0216K3Z-FL-GBW-V3 LCD display over I2C on Raspberry Pi.
The module provides functions for all commands from the NHD-0216K3Z-FL-GBW-V3 datasheet.

## Installation
Download NHD_0216K3Z.py and add it to your Python project.
The Python library smbus must also be installed.

## Usage
``` python
from NHD_0216K3Z import NHD_0216K3Z 
from smbus import SMBus

DEVICE_BUS = 1
DEVICE_ADDR = 0x0A
bus = SMBus(DEVICE_BUS)
lcd = NHD_0216K3Z(bus, DEVICE_ADDR)
lcd.display_on()
lcd.disp_msg("Hello World!") 
```



