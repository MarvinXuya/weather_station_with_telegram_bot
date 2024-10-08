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
import ngrok_setup
# weathersastion
import datetime
import get_bme280
import get_si7021
import get_ds18b20
# weather sources
import weather_collector
# covid data
import covid
# system
import socket

# bot conf
CONFIG = json.loads(open('/home/pi/weather_station_with_telegram_bot\
/config_files/config.json', 'r').read())
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
MYSQL_USER = CONFIG['mysql_user']
MYSQL_PASSWORD = CONFIG['mysql_password']
MYSQL_DATABASE = CONFIG['mysql_database']
COUNTRY = CONFIG['COUNTRY']
add_bme280 = CONFIG['bme280']
add_ds18b20 = CONFIG['ds18b20']
add_si7021 = CONFIG['si7021']
weather_collectors = CONFIG['weather_collectors']
source_name = CONFIG["source_name"]

# Tunnel conf
public_url = ""
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


def get_date():
    date = datetime.datetime.now()
    now = str(date.strftime("%Y-%m-%d %H:%M:%S")) + "\n"
    return now


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
                   + '\n /update_users'
                   + '\n /reboot'
                   + '\n /grafana'
                   + '\n /ip'
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
        message = (get_date() + ngrok_setup.connect_tunnel)
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
        message = (get_date() + ngrok_setup.disconnect_tunnel)
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
        message = (get_date() + ngrok_setup.get_tunnels)
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
        try:
            connection = MySQLdb.connect(user=MYSQL_USER,
                                         password=MYSQL_PASSWORD,
                                         database=MYSQL_DATABASE)
        except connection.error:
            message = (get_date()
                       + "\n No puedo comunicarme con mi base de datos.")
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
        message = (get_date()
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


def covid_data(bot: telegram.Bot, update: telegram.Update):
    if (update.message.from_user.id in USER) or \
       (update.message.from_user.id in COVID_USER):
        try:
            update.message.reply_text("Updating data, will be back soon")
            message = (get_date() + covid.get_data(COUNTRY))
            update.message.reply_text("Data updated")
            update.message.reply_text(message)
        except logging.error:
            logging.error('Not able to get data')


def covid_link(bot: telegram.Bot, update: telegram.Update):
    if (update.message.from_user.id in USER) \
       or (update.message.from_user.id in COVID_USER):
        message = "https://www.bing.com/covid/local/{}".format(COUNTRY.lower())
        update.message.reply_text(message)


# Get current data from sensors who are active
def get_weather(bot: telegram.Bot, update: telegram.Update):
    print(update.message.from_user)
    if update.message.from_user.id in USER:
        try:
            if add_bme280 is True:
                bme280_success = False
                if 'bme280data' not in vars():
                    try:
                        bme280data = get_bme280.get_bme280()
                        bme280_success = True
                    except AssertionError:
                        bme280msg = ''
                if bme280_success is True:
                    bme280msg = ("\nHumidity: "
                                 + str(round(bme280data.humidity, 2))
                                 + "%"
                                 + "\nPresure: "
                                 + str(round(bme280data.pressure, 2))
                                 + "\nTemperature: "
                                 + str(round(bme280data.temperature, 2)) + "C")
                else:
                    bme280msg = ''
            else:
                bme280msg = ''
            if add_si7021 is True:
                si7021_success = False
                if 'si7021data' not in vars():
                    try:
                        si7021data = get_si7021.get_si7021()
                        si7021_success = True
                    except AssertionError:
                        si7021msg = ''
                if si7021_success is True:
                    si7021msg = ("\nTemperature SI7021: "
                                 + "%0.1f C" % si7021data.temperature
                                 + "\nHumidity: "
                                 + "%0.1f %%" % si7021data.relative_humidity)
                else:
                    si7021msg = ''
            else:
                si7021msg = ''
            if add_ds18b20 is True:
                ds18b20_success = False
                if 'ds18b20data' not in vars():
                    try:
                        ds18b20data = get_ds18b20.get_ds18b20()
                        ds18b20_success = True
                    except AssertionError:
                        ds18b20msg = ''
                if ds18b20_success is True:
                    ds18b20msg = ("\nDS18B20: "
                                  + str(round(ds18b20data, 2)) + 'C')
                else:
                    ds18b20msg = ''
            else:
                ds18b20msg = ''
            message = (get_date()
                       + "Source: " + source_name
                       + bme280msg
                       + si7021msg
                       + ds18b20msg
                       + weather_collector.get_collectors(weather_collectors))
            update.message.reply_text(message)
        except Exception as e:
            logging.error("Not able to get data from artifacts: {}\n".format(
                          str(e)))
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


def reboot(bot: telegram.Bot, update: telegram.Update):
    print(update.message.from_user)
    if update.message.from_user.id in ADMIN_USER:
        os.system("sudo reboot now")
    else:
        reply_deny_message = 'Ops! ' + str(update.message.from_user.first_name)
        +' you are not allowed to do it.'
        update.message.reply_text(reply_deny_message)
        unknown_user(update.message.from_user.id,
                     update.message.from_user.first_name)


def get_ip(bot: telegram.Bot, update: telegram.Update):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    message = "Data from {}: {}".format(get_date(), IP)
    update.message.reply_text(message)

def grafana(bot: telegram.Bot, update: telegram.Update):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    message = "Data date: {}http://{}:3000".format(get_date(), IP)
    update.message.reply_text(message)

# Place actions
dispatcher.add_handler(CommandHandler(['hello', 'start'], echo_start))
dispatcher.add_handler(CommandHandler('weather', get_weather))
dispatcher.add_handler(CommandHandler('tunnel', connect_tunnel))
dispatcher.add_handler(CommandHandler('stop_tunnel', disconnect_tunnel))
dispatcher.add_handler(CommandHandler('check_tunnels', get_tunnels))
dispatcher.add_handler(CommandHandler('check_db', get_last_data))
dispatcher.add_handler(CommandHandler('covid', covid_data))
dispatcher.add_handler(CommandHandler('covid_link', covid_link))
dispatcher.add_handler(CommandHandler('update_users', update_users))
dispatcher.add_handler(CommandHandler('reboot', reboot))
dispatcher.add_handler(CommandHandler('ip', get_ip))
dispatcher.add_handler(CommandHandler('grafana', grafana))


# Start bot
updater.start_polling()
updater.idle()
