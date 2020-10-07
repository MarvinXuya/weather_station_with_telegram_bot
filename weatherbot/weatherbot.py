# telegram bot
import os
import telegram
from telegram.ext import Updater, CommandHandler
import json
# logs
import logging
import logging.handlers
import gzip
# if mysql is setup
import MySQLdb
# tunnel
from pyngrok import ngrok
# weathersastion
import glob
import time
import bme280
import smbus2
import datetime
#

# bot conf
CONFIG = json.loads(open('./config_files/config.json', 'r').read())
updater = Updater(token=CONFIG['token'])
dispatcher = updater.dispatcher
jobqueue = updater.job_queue
me = updater.bot.get_me()
CONFIG['user_name'] = '@' + me.username
ADMIN_USER = CONFIG['admin']
USER = CONFIG['allowed']
COVID_USER = CONFIG['covid']
LOG_PATH = CONFIG['log_path']
UNKNOWN_USERS_PATH = CONFIG['unknown_path']
NGROK_TOKEN = CONFIG['ngrok_token']
MYSQL_USER = CONFIG['mysql_user']
MYSQL_PASSWORD = CONFIG['mysql_password']
MYSQL_DATABASE = CONFIG['mysql_database']
data = ""
totalRecovered = ""
totalConfirmed = ""
totalDeaths = ""
lastUpdated = ""
# Tunnel conf
public_url = ""
ngrok.set_auth_token(NGROK_TOKEN)


def echo_start(bot: telegram.Bot, update: telegram.Update):
    print(update.message.from_user)
    if update.message.from_user.id in ADMIN_USER:
        message = ('Welcome to the mx madhouse'
                   + '\nMy options are:'
                   + '\n /hello'
                   + '\n /weather'
                   + '\n /tunnel'
                   + '\n /stop_tunnel'
                   + '\n /check_tunnels'
                   + '\n /check_db'
                   + '\n /covid'
                   + '\n /covid_link'
                   + '\n /covid_update'
                   + '\n /update_users'
                   )
        update.message.reply_text(message)
    elif update.message.from_user.id in USER:
        message = ('Welcome to the mx madhouse'
                   + '\nMy options are:'
                   + '\n /hello'
                   + '\n /weather'
                   + '\n /tunnel'
                   + '\n /stop_tunnel'
                   + '\n /check_tunnels'
                   + '\n /check_db'
                   + '\n /covid'
                   + '\n /covid_link'
                   + '\n /covid_update'
                   )
        update.message.reply_text(message)
    elif update.message.from_user.id in COVID_USER:
        message = ('Welcome to the mx madhouse'
                   + '\nMy options are:'
                   + '\n /hello'
                   + '\n /covid'
                   )
        update.message.reply_text(message)
    else:
        reply_deny_message = 'Ops! '
        + str(update.message.from_user.first_name)
        + ' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,
                     update.message.from_user.first_name)


def update_users(bot: telegram.Bot, update: telegram.Update):
    global ADMIN_USER
    if update.message.from_user.id in ADMIN_USER:
        global USER
        global COVID_USER
        CONFIG = json.loads(open('./config_files/config.json', 'r').read())
        USER = CONFIG['allowed']
        COVID_USER = CONFIG['covid']
        ADMIN_USER = CONFIG['admin']
        update.message.reply_text('Users updated')
    else:
        reply_deny_message = 'Ops! ' + str(update.message.from_user.first_name)
        +' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,
                     update.message.from_user.first_name)


def connect_tunnel(bot: telegram.Bot, update: telegram.Update):
    if update.message.from_user.id in USER:
        global public_url
        date = datetime.datetime.now()
        now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        public_url = ngrok.connect(3000)
        message = (now + "\nURL: " + public_url)
        update.message.reply_text(message)
    else:
        reply_deny_message = 'Ops! '
        + str(update.message.from_user.first_name)
        + ' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,
                     update.message.from_user.first_name)


def disconnect_tunnel(bot: telegram.Bot, update: telegram.Update):
    if update.message.from_user.id in USER:
        global public_url
        date = datetime.datetime.now()
        now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        ngrok.disconnect(public_url)
        ngrok.kill()
        tunnels = ngrok.get_tunnels()
        message = (now + "\nactive: " + str(tunnels))
        update.message.reply_text(message)
    else:
        reply_deny_message = 'Ops! '
        + str(update.message.from_user.first_name)
        + ' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,
                     update.message.from_user.first_name)


def get_tunnels(bot: telegram.Bot, update: telegram.Update):
    if update.message.from_user.id in USER:
        tunnels = ngrok.get_tunnels()
        date = datetime.datetime.now()
        now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        message = (now + "\nactive: " + str(tunnels))
        update.message.reply_text(message)
    else:
        reply_deny_message = 'Ops! '
        + str(update.message.from_user.first_name)
        + ' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,
                     update.message.from_user.first_name)


def get_last_data(bot: telegram.Bot, update: telegram.Update):
    if update.message.from_user.id in USER:
        date = datetime.datetime.now()
        now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        try:
            connection = MySQLdb.connect(user=MYSQL_USER,
                                         password=MYSQL_PASSWORD,
                                         database=MYSQL_DATABASE)
        except connection.error:
            message = (now + "\n No puedo comunicarme con mi base de datos.")
            update.message.reply_text(message)
        cursor = connection.cursor()
        cursor.execute("""SELECT date_time,humedad,presion,temperatura,
                          temperatura_DS18B20 FROM botdata ORDER BY date_time
                          DESC LIMIT 1;""")
        result = cursor.fetchone()
        connection.commit()
        connection.close()
        date_time = result[0]
        humedad = result[1]
        presion = result[2]
        temperatura = result[3]
        temperatura_DS18B20 = result[4]
        message = (now
                   + "\nUltima fecha: " + str(date_time)
                   + "\nHumedad: " + str(humedad)
                   + "\nPresion: " + str(presion)
                   + "\nTemperatura: " + str(temperatura)
                   + "\nTemperatura_DS18B20: " + str(temperatura_DS18B20)
                   )
        update.message.reply_text(message)
    else:
        reply_deny_message = 'Ops! '
        + str(update.message.from_user.first_name)
        +' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,
                     update.message.from_user.first_name)


# Logs
log_f = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,
                    format=log_f,
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=LOG_PATH)


# Log rotate class
class GZipRotator:
    def __call__(self, source, dest):
        os.rename(source, dest)
        f_in = open(dest, 'rb')
        f_out = gzip.open("%s.gz" % dest, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(dest)


# Log setup
logformatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s')
log = logging.handlers.TimedRotatingFileHandler(LOG_PATH, 'midnight',
                                                1, backupCount=5)
log.setLevel(logging.DEBUG)
log.setFormatter(logformatter)
log.rotator = GZipRotator()
logger = logging.getLogger('main')
logger.addHandler(log)
# logger.setLevel(logging.DEBUG)


def write_json(data, filename=UNKNOWN_USERS_PATH):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def unknown_user(id, name):
    result = False
    unknown_data = json.loads(open(UNKNOWN_USERS_PATH, 'r').read())
    for count, _name in enumerate(unknown_data):
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


def update_data(bot: telegram.Bot, update: telegram.Update):
    if (update.message.from_user.id in USER) or \
       (update.message.from_user.id in COVID_USER):
        try:
            update.message.reply_text("Updating data, will be back soon")
            raw = os.popen("bash /home/pi/get_data.sh")
        except logging.error:
            logging.error('Not able to get data')
        global totalRecovered
        global totalConfirmed
        global totalDeaths
        global lastUpdated
        try:
            data = json.loads(raw.read())
        except logging.error:
            logging.error('Not able to load json')
        totalRecovered = data.get('totalRecovered')
        totalConfirmed = data.get('totalConfirmed')
        totalDeaths = data.get('totalDeaths')
        lastUpdated = data.get('lastUpdated')
        update.message.reply_text("Data updated")
        date = datetime.datetime.now()
        now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        active = totalConfirmed - totalRecovered - totalDeaths
        message = ("Guatemala {}\nActive:  {}\nConfirmed: {}\nRecovered:\
        {}\nDeaths: {}\nDate: {}").format(now, active, totalConfirmed,
                                          totalRecovered, totalDeaths,
                                          lastUpdated)
        update.message.reply_text(message)


def covid_link(bot: telegram.Bot, update: telegram.Update):
    if (update.message.from_user.id in USER) \
       or (update.message.from_user.id in COVID_USER):
        message = "https://www.bing.com/covid/local/guatemala"
        update.message.reply_text(message)


def covid(bot: telegram.Bot, update: telegram.Update):
    if (update.message.from_user.id in USER) or \
       (update.message.from_user.id in COVID_USER):
        date = datetime.datetime.now()
        now = str(date.strftime("%Y-%m-%d %H:%M:%S"))
        active = totalConfirmed - totalRecovered - totalDeaths
        message = ("Guatemala {}\nActive: {}\nConfirmed: {}\nRecovered: \
        {}\nDeadths: {}\nDate: {}").format(now, active, totalConfirmed,
                                           totalRecovered, totalDeaths,
                                           lastUpdated)
        update.message.reply_text(message)


def get_weather(bot: telegram.Bot, update: telegram.Update):
    print(update.message.from_user)
    if update.message.from_user.id in USER:
        port = 1
        address = 0x77  # Adafruit BME280 address. Other may be different
        check = 0
        try:
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
                       + "\n             ds18b20: " + "%s C" % obj.read_temp()
                       )
            update.message.reply_text(message)
        except Exception as e:
            logging.error("Not able to get data from artifacts: {}\n".format(
                          str(e)))
            if 'bus' in locals():
                bus.close()
            something_wrong = 'Ops! '
            + str(update.message.from_user.first_name)
            + ' there was a problem trying to collect weather data.'
            update.message.reply_text(something_wrong)
    else:
        reply_deny_message = 'Ops! '
        + str(update.message.from_user.first_name)
        + ' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,
                     update.message.from_user.first_name)


# Place actions
dispatcher.add_handler(CommandHandler(['hello', 'start'], echo_start))
dispatcher.add_handler(CommandHandler('weather', get_weather))
dispatcher.add_handler(CommandHandler('tunnel', connect_tunnel))
dispatcher.add_handler(CommandHandler('stop_tunnel', disconnect_tunnel))
dispatcher.add_handler(CommandHandler('check_tunnels', get_tunnels))
dispatcher.add_handler(CommandHandler('check_db', get_last_data))
dispatcher.add_handler(CommandHandler('covid_update', update_data))
dispatcher.add_handler(CommandHandler('covid', covid))
dispatcher.add_handler(CommandHandler('covid_link', covid_link))
dispatcher.add_handler(CommandHandler('update_users', update_users))

# Start bot
updater.start_polling()
updater.idle()
