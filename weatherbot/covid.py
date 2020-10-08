# Covid data from bing
import subprocess
import json


def get_data(country):
    path_to_script = '/home/pi/weather_station_with_telegram_bot\
/bin/get_data.sh'
    args = ['bash', path_to_script, country.lower()]
    try:
        res = subprocess.Popen(args, stdout=subprocess.PIPE)
        res.wait()
        if res.returncode != 0:
            message = "Exit status from  script {}\n".format(res.returncode)
            return message
        result = res.stdout.read()
        try:
            data = json.loads(result)
            totalRecovered = data.get('totalRecovered')
            totalConfirmed = data.get('totalConfirmed')
            totalDeaths = data.get('totalDeaths')
            lastUpdated = data.get('lastUpdated')
            active = totalConfirmed - totalRecovered - totalDeaths
            message = ("\n"+country.capitalize() + ":\n- Active: {}\n- Confirmed: {}\n- Recovered:\
 {}\n- Deaths: {}\n- Data date: {}").format(active, totalConfirmed,
                                            totalRecovered, totalDeaths,
                                            lastUpdated)
            return message
        except Exception:
            message = 'Not able to load json'
            return message
    except OSError:
        message = 'Not able to run script to get data'
        return message
