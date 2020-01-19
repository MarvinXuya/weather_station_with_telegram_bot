# bot
import os
import logging
import telegram
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
import json
#

# Inicio weather
import glob, time
import bme280
import smbus2
from time import sleep
import datetime
#

# bot conf
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='/var/log/chango_leon.log')
CONFIG = json.loads(open('./templates/config.json', 'r').read())

updater = Updater(token = CONFIG['token'])
dispatcher = updater.dispatcher
jobqueue = updater.job_queue
me = updater.bot.get_me()
CONFIG['username'] = '@' + me.username
USER = CONFIG['allowed']

def echo_start(bot : telegram.Bot, update : telegram.Update):
    print(update.message.from_user)
    if update.message.from_user.id in USER:
        update.message.reply_text('Welcome to the mx madhouse')
    else:
        update.message.reply_text('Ops! you are not allowed')

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

def get_weather(bot : telegram.Bot, update : telegram.Update):
    print(update.message.from_user)
    if update.message.from_user.id in USER:
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
        update.message.reply_text(str(now.strftime("%Y-%m-%d %H:%M:%S")))
        update.message.reply_text("Humedad: " + str(round(humidity,2))+ "%" )
        update.message.reply_text("Presion: " + str(round(pressure,2)))
        update.message.reply_text("Temperatura: " + str(round(ambient_temperature,2)) +  " - Temp2: %s C" % obj.read_temp())
    else:
        update.message.reply_text('Ops! you are not allowed')

# Place actions
dispatcher.add_handler(CommandHandler('start', echo_start))
dispatcher.add_handler(CommandHandler('weather', get_weather))
# Start bot
updater.start_polling()
updater.idle()
