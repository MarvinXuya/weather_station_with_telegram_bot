# bot
import json
import MySQLdb
# Starting weather
import glob
import time
import get_bme280
import get_ds18b20
from time import sleep
import datetime

CONFIG = json.loads(open('/home/pi/weather_station_with_telegram_bot\
/config_files/config.json', 'r').read())
MYSQL_USER = CONFIG['mysql_user']
MYSQL_PASSWORD = CONFIG['mysql_password']
MYSQL_DATABASE = CONFIG['mysql_database']

# logs

# Logs
logf = open("/var/log/mysql_chango.log", "w")


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


port = 1
address = 0x77  # Adafruit BME280 address. Other BME280s may be different
while True:
    try:
        bme280data = get_bme280.get_bme280()
    except Exception as e:
        logf.write("Not able to get data from bme280: {}\n".format(e))
    try:
        humidity = bme280data.humidity
    except Exception as e:
        logf.write("Not able to assign humidity from bme280: {}\n".format(e))
    try:
        pressure = bme280data.pressure
    except Exception as e:
        logf.write("Not able to assign pressure from bme280: {}\n".format(e))
    try:
        ambient_temperature = bme280data.temperature
    except Exception as e:
        logf.write("Not able to assign temperature "
                   + "from bme280: {}\n".format(e))
    try:
        ds18b20data = get_ds18b20.get_ds18b20()
    except Exception as e:
        logf.write("Not able to get data from ds18b20: {}\n".format(e))
        continue
    now = datetime.datetime.now()
    try:
        connection = MySQLdb.connect(user=MYSQL_USER,
                                     password=MYSQL_PASSWORD,
                                     database=MYSQL_DATABASE)
        cursor = connection.cursor()
        cursor.executemany(
              """INSERT INTO botdata (date_time, humedad, presion,
              temperatura, temperatura_DS18B20)
              VALUES (%s, %s, %s, %s, %s)""",
              [(now, humidity, pressure, ambient_temperature,
                ds18b20data)])
        connection.commit()
        connection.close()
    except Exception as e:
        logf.write("Not able to connect to database: {}\n".format(str(e)))
        if (connection):
            connection.close()
        else:
            logf.write("There is no need to close connection on database")
        continue
    sleep(600)
