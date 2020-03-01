# bot
import os
import logging
import telegram
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
import json
#if mysql is setup
import MySQLdb
#tunnel
from pyngrok import ngrok


# Inicio weather
import glob, time
import bme280
import smbus2
from time import sleep
import datetime
#

# bot conf
CONFIG = json.loads(open('./config_files/config.json', 'r').read())
updater = Updater(token = CONFIG['token'])
dispatcher = updater.dispatcher
jobqueue = updater.job_queue
me = updater.bot.get_me()
CONFIG['user_name'] = '@' + me.username
USER = CONFIG['allowed']
LOG_PATH = CONFIG['log_path']
UNKNOWN_USERS_PATH=CONFIG['unknown_path']
NGROK_TOKEN = CONFIG['ngrok_token']

# Tunnel conf
public_url=""
ngrok.set_auth_token(NGROK_TOKEN)
def connect_tunnel(bot : telegram.Bot, update : telegram.Update):
    global public_url
    date = datetime.datetime.now()
    now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
    public_url = ngrok.connect(3000)
    message = ( now
    + "\nURL: " + public_url
    )
    update.message.reply_text(message)

def disconnect_tunnel(bot : telegram.Bot, update : telegram.Update):
    global public_url
    date = datetime.datetime.now()
    now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
    ngrok.disconnect(public_url)
    ngrok.kill()
    tunnels = ngrok.get_tunnels()
    message = ( now
    + "\nactive: " + str(tunnels)
    )
    update.message.reply_text(message)

def get_tunnels(bot : telegram.Bot, update : telegram.Update):
    tunnels = ngrok.get_tunnels()
    date = datetime.datetime.now()
    now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
    message = ( now
    + "\nactive: " + str(tunnels)
    )
    update.message.reply_text(message)

# Logs
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=LOG_PATH)



def echo_start(bot : telegram.Bot, update : telegram.Update):
    print(update.message.from_user)
    if update.message.from_user.id in USER:
        update.message.reply_text('Welcome to the mx madhouse')
    else:
        reply_deny_message='Ops! ' + str(update.message.from_user.first_name) +' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,update.message.from_user.first_name)


def write_json(data, filename=UNKNOWN_USERS_PATH):
    with open(filename,'w') as f:
        json.dump(data, f, indent=4)

def unknown_user(id, name):
    result=False
    unknown_data = json.loads(open(UNKNOWN_USERS_PATH, 'r').read())
    for count,_name in enumerate(unknown_data):
        if unknown_data[count].get('id') != id:
            result = True
        else:
            result = False

    if result:
        print('escribiendo: ' + str(id) + str(name))
        with open(UNKNOWN_USERS_PATH) as json_file:
            data = json.load(json_file)
            temp = data
            y = {"name": name,
             "id": id
            }
            # appending data to emp_details
            temp.append(y)
        write_json(data)


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
        humidity = str(round(bme280_data.humidity,2))+ "%"
        pressure = str(round(bme280_data.pressure,2))
        ambient_temperature = str(round(bme280_data.temperature,2)) +  "C"
        date = datetime.datetime.now()
        now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        obj = DS18B20()
        message = ( now
        + "\nHumedad: " + humidity
        + "\nPresion: " + pressure
        + "\nTemperatura: "
        + "\n             bme280:  " +  ambient_temperature
        + "\n             ds18b20: " +  "%s C" % obj.read_temp()
        )
        update.message.reply_text(message)
    else:
        reply_deny_message='Ops! ' + str(update.message.from_user.first_name) +' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,update.message.from_user.first_name)

# Place actions
dispatcher.add_handler(CommandHandler('start', echo_start))
dispatcher.add_handler(CommandHandler('weather', get_weather))
dispatcher.add_handler(CommandHandler('grafana', connect_tunnel))
dispatcher.add_handler(CommandHandler('disconnect_grafana', disconnect_tunnel))
dispatcher.add_handler(CommandHandler('tunnels', get_tunnels))

# Start bot
updater.start_polling()
updater.idle()
