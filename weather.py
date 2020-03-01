# bot
import os
import logging
import json
import MySQLdb
#

# Inicio weather
import glob, time
import bme280
import smbus2
from time import sleep
import datetime
#

CONFIG = json.loads(open('./config_files/config.json', 'r').read())
MYSQL_USER = CONFIG['mysql_user']
MYSQL_PASSWORD = CONFIG['mysql_password']
MYSQL_DATABASE = CONFIG['mysql_database']


class DS18B20(object):
    def __init__(self):
        self.device_file = glob.glob("/sys/bus/w1/devices/28*")[0] + "/w1_slave"

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

while True:
    port = 1
    address = 0x77 # Adafruit BME280 address. Other BME280s may be different
    bus = smbus2.SMBus(port)
    bme280.load_calibration_params(bus,address)
    global chat_id
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    now = datetime.datetime.now()
    obj = DS18B20()
    temperatura_DS18B20 = obj.read_temp()
    connection = MySQLdb.connect(user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor=connection.cursor()
    cursor.executemany(
          """INSERT INTO botdata (date_time, humedad, presion, temperatura, temperatura_DS18B20)
          VALUES (%s, %s, %s, %s, %s)""",
          [(now,humidity,pressure,ambient_temperature,temperatura_DS18B20)] )
    connection.commit()
    connection.close()
    sleep(600)
