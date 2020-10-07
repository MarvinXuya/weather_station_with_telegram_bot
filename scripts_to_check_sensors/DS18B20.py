# DS18B20 - smbus2
# Make sure this is properly set:
# sudo echo w1-gpio >> /etc/modules
# sudo echo w1-therm >> /etc/modules
# sudo echo dtoverlay=w1-gpio >> /boot/config.txt
# It will test two sensors

import glob
import time
import bme280
import smbus2
import datetime


class DS18B20(object):
    def __init__(self):
        self.device_file = glob.glob("/sys/bus/w1/devices/28*")[0]
        + "/w1_slave"

    def read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        f.close()
        return lines

    def crc_check(self, lines):
        return lines[0].strip()[-3:] == "YES"

    def read_temp(self):
        temp_c = -255
        attempts = 0

        lines = self.read_temp_raw()
        success = self.crc_check(lines)

        while not success and attempts < 3:
            time.sleep(.2)
            lines = self.read_temp_raw()
            success = self.crc_check(lines)
            attempts += 1

        if success:
            temp_line = lines[1]
            equal_pos = temp_line.find("t=")
            if equal_pos != -1:
                temp_string = temp_line[equal_pos+2:]
                temp_c = float(temp_string)/1000.0
        return temp_c


obj = DS18B20()
print(obj.read_temp())
port = 1
address = 0x77  # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)
bme280.load_calibration_params(bus, address)
global chat_id
bme280_data = bme280.sample(bus, address)
humidity = str(round(bme280_data.humidity, 2)) + "%"
pressure = str(round(bme280_data.pressure, 2))
ambient_temperature = str(round(bme280_data.temperature, 2)) + "C"
date = datetime.datetime.now()
now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
obj = DS18B20()
message = (now
           + "\nHumedad: " + humidity
           + "\nPresion: " + pressure
           + "\nTemperatura: "
           + "\n             bme280:  " + ambient_temperature
           )
print(message)
