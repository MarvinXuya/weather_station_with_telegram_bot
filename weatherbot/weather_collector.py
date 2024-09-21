# weather_collector.py

import requests
import socket

def get_data(url):
    try:
        x = requests.get(url, timeout=5)
        if x.status_code == 200:
            return x.json()
    except:
        print ('*************Something went wrong calling ' + url)
        pass


def get_collectors(weather_collectors):
    message = ""
    for collector in weather_collectors:
        try:
            ip = socket.gethostbyname(collector['hostname'])
            url = "http://{}:1985/weather".format(str(ip))
            data = get_data(url)
            message += (
                        "\n------------------"
                        + "\nSource: " + collector['name']
                        + "\nHumidity: "
                        + str(data['Humidity'])
                        + "\nPresure: "
                        + str(data['Pressure'])
                        + "\nTemperature: "
                        + str(data['Temperature'])
                        + "\nDS18D20: "
                        + str(data['ds18b20']))
        except:
            message += '\n------------------\nSomething went wrong collecting data from ' + collector['name']
            pass
    if (message == ""):
        return "\n------------------\nSomething went wrong collecting data"
    else:
        return(message)
