# mysql
import json
import MySQLdb
# sensors
import get_bme280
import get_ds18b20
import get_si7021
# times
from time import sleep
import datetime
# initial vars
conf_p = "/home/pi/weather_station_with_telegram_bot/config_files/config.json"
config = json.loads(open(conf_p, 'r').read())
mysql_user = config['mysql_user']
mysql_password = config['mysql_password']
mysql_database = config['mysql_database']
add_bme280 = config['bme280']
add_ds18b20 = config['ds18b20']
add_si7021 = config['si7021']
sleep_time = config['sleep_time_data_collector_secs']
# Logs
logf = open("/var/log/mysql_chango.log", "w")
# main
logf.write("Starting data collect with values:" +
           "\n- BME280: {}\n".format(add_bme280) +
           "\n- DS18b20: {}\n".format(add_ds18b20) +
           "\n- SI7021: {}\n".format(add_si7021) +
           "\n- Sleep time: {}\n".format(sleep_time))
while True:
    # sensors interaction
    if add_si7021 is True:
        if 'si7021data' not in vars():
            try:
                si7021data = get_si7021.get_si7021()
            except AssertionError as error:
                logf.write("Not able to get data from si7021" +
                           ": {}\n".format(error))
                temperature = None
                humidity = None
                pressure = None
                continue
        temperature = si7021data.temperature
        humidity = si7021data.relative_humidity
        pressure = None
        add_bme280 = False
    if add_bme280 is True:
        if 'bme280data' not in vars():
            try:
                bme280data = get_bme280.get_bme280()
            except AssertionError as error:
                logf.write("Not able to get data from bme280" +
                           ": {}".format(error))
                temperature = None
                humidity = None
                pressure = None
                continue
        try:
            humidity = bme280data.humidity
        except AssertionError as error:
            logf.write("Not able to assign humidity from bme280:"
                       + " {}\n".format(error))
            humidity = None
        try:
            pressure = bme280data.pressure
        except AssertionError as error:
            logf.write("Not able to assign pressure from bme280:"
                       + " {}\n".format(error))
            pressure = None
        try:
            temperature = bme280data.temperature
        except AssertionError as error:
            logf.write("Not able to assign temperature "
                       + "from bme280: {}\n".format(error))
            temperature = None
    if add_si7021 is False and add_bme280 is False:
        humidity = None
        pressure = None
        temperature = None
    if add_ds18b20 is True:
        try:
            temperature_ds18b20 = get_ds18b20.get_ds18b20()
        except AssertionError as error:
            logf.write("Not able to get data from ds18b20: {}\n".format(error))
            temperature_ds18b20 = None
            continue
    else:
        temperature_ds18b20 = None
    now = datetime.datetime.now()
    # database interaction
    try:
        connection = MySQLdb.connect(user=mysql_user,
                                     password=mysql_password,
                                     database=mysql_database)
    except Exception as e:
        logf.write("Not able to connect to database: {}\n".format(str(e)))
        if (connection):
            connection.close()
        else:
            logf.write("There is no need to close connection on database")
        continue
    try:
        cursor = connection.cursor()
        cursor.executemany(
              """INSERT INTO botdata (date_time, humedad, presion,
              temperatura, temperatura_DS18B20)
              VALUES (%s, %s, %s, %s, %s)""",
              [(now, humidity, pressure, temperature,
                temperature_ds18b20)])
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        logf.write("Not able to insert to database: {}\n".format(str(e)))
        if (connection):
            connection.close()
        else:
            logf.write("There is no need to close connection on database")
        continue
    sleep(sleep_time)
