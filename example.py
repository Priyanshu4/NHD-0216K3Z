from NHD_0216K3Z import NHD_0216K3Z 
from smbus import SMBus

DEVICE_BUS = 1
DEVICE_ADDR = 0x0A
bus = SMBus(DEVICE_BUS)
lcd = NHD_0216K3Z(bus, DEVICE_ADDR)
lcd.disp_msg("Hello World!") 
