# Ngrok interaction
from pyngrok import ngrok
import json

CONFIG = json.loads(open('/home/pi/weather_station_with_telegram_bot\
/config_files/config.json', 'r').read())
NGROK_TOKEN = CONFIG['ngrok_token']
ngrok.set_auth_token(NGROK_TOKEN)


def connect_tunnel():
    public_url = ngrok.connect(3000)
    message = ("\nURL: " + public_url)
    return message


def disconnect_tunnel():
    tunnels = ngrok.get_tunnels()
    public_url = (tunnels.split("NgrokTunnel: ",
                  maxsplit=1)[-1].split(maxsplit=1)[0].strip('"'))
    ngrok.disconnect(public_url)
    ngrok.kill()
    tunnels_check = ngrok.get_tunnels()
    message = ("\nInitial tunnels: " + str(tunnels)
               + "\nFinal tunnels: " + str(tunnels_check))
    return message


def get_tunnels():
    tunnels = ngrok.get_tunnels()
    message = ("\nActive tunnels: " + str(tunnels))
    return message
