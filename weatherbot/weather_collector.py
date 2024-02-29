# weather_collector.py

import requests


def get_data(url):
    try:
        x = requests.get(url, timeout=5)
        if x.status_code == 200:
            return x.json()
    except Exception:
        print('Something went wrong calling ' + url)


def get_collectors(weather_collectors):
    try:
        message = ""
        for collector in weather_collectors:
            data = get_data(collector["url"])
            message += (
                        "\n------------------"
                        + "\nSource: " + collector['name']
                        + "\nPresure: "
                        + str(data['Presure'])
                        + "\nTemperature: "
                        + str(data['Temperature'])
                        + "\nHumidity: "
                        + str(data['humidity']))
        return(message)
    except Exception:
        return '\nSomething went wrong collecting data'

