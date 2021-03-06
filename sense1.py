# See https://docs.pycom.io for more information regarding library specifics
from network import LoRa
#import config
from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE
import time   # import library for delay times
import pycom
import socket
import binascii
import struct

import ujson


# Colors
off = 0x000000
red = 0xff0000
green = 0x00ff00
blue = 0x0000ff
yellow = 0xffff00

# Initialize LoRa in LORAWAN mode.
# Initialize LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AU915)

# Turn off hearbeat LED
pycom.heartbeat(False)

# create an ABP authentication params
dev_addr = struct.unpack(">l", binascii.unhexlify('26 06 22 DD'.replace(' ','')))[0]
nwk_swkey = binascii.unhexlify('F088B79348D05C782F749BFE9D105220'.replace(' ',''))
app_swkey = binascii.unhexlify('647706A5E324855B638E99E9D018B8A2'.replace(' ',''))

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

while not lora.has_joined():
    time.sleep(1)
    print('Waiting to Join LoRaWAN Network...')

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)

# Builds the bytearray to send the request
py = Pysense()
si = SI7006A20(py)
lt = LTR329ALS01(py)
li = LIS2HH12(py)

for count in range (2000):
    print("Count=", count)
    vt = py.read_battery_voltage()
    print("Battery voltage: " +str(vt))
    dew = si.dew_point()
    print("Dew point: "+ str(dew) + " deg C")
#   mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
#    print("MPL3115A2 temperature: " + str(mp.temperature()))
    temp1 = 35.3 #mp.temperature()
    alt1 = 90.2 # mp.altitude()+100.0
    print("Altitude: " + str(alt1))
#    mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
    press1 = 1001.3 #mpp.pressure()
    print("Pressure: " + str(press1)) #Pressure does not work too well
    temp2 = si.temperature()
    hum1 = si.humidity()
    print("Temperature: " + str(temp2)+ " deg C and Relative Humidity: " + str(hum1) + " %RH")
    t_ambient = 24.4
    relhum = si.humid_ambient(t_ambient)
    print("Humidity Ambient for " + str(t_ambient) + " deg C is " + str(relhum) + "%RH")
    print("Light (channel Blue lux, channel Red lux): " + str(lt.light()))
    acct = li.acceleration()
    acc1 = acct[0]
    acc2 = acct[1]
    acc3 = acct[2]
    roll1 = li.roll()
    pitch1 = li.pitch()
    print("Acceleration: " + str(acc1))
    print("Roll: " + str(roll1))
    print("Pitch: " + str(pitch1))
    # Flash the light every time a payload is sent
    pycom.rgbled(blue)
    time.sleep(0.5)
    pycom.rgbled(off)
    time.sleep(0.5)
    pycom.rgbled(red)
    time.sleep(0.5)
    pycom.rgbled(off)
    data = bytearray(48)
    data[0:4] = bytearray(struct.pack(">i", count))
    data[4:8] = bytearray(struct.pack(">f", vt))
    data[8:12] = bytearray(struct.pack(">f", dew))
    data[12:16] = bytearray(struct.pack(">f", temp1))
    data[16:20] = bytearray(struct.pack(">f", alt1))
    data[20:24] = bytearray(struct.pack(">f", press1))
    data[24:28] = bytearray(struct.pack(">f", temp2))
    data[28:32] = bytearray(struct.pack(">f", hum1))
    data[32:36] = bytearray(struct.pack(">f", relhum))
    data[36:40] = bytearray(struct.pack(">f", acc1))
    data[40:44] = bytearray(struct.pack(">f", acc2))
    data[44:48] = bytearray(struct.pack(">f", acc3))
#    data[48:52] = bytearray(struct.pack(">f", roll1))
#    data[52:56] = bytearray(struct.pack(">f", pitch1))
    print ('Data = ',count,vt,dew, temp1, alt1, press1, temp2, hum1, relhum, acc1, acc2, acc3, roll1, pitch1 )
    s.setblocking(True)
    s.send(data)  # send buffer to AWS
    print('data sent')
    time.sleep(0.5)
    # get any data received&
    s.setblocking(False)
    data = s.recv(64)
    time.sleep(0.5)
    print(data)  #anything received?time.sleep(20)  # wait time between packets sent
    time.sleep(59)
