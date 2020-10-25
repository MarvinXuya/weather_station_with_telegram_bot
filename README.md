# Weather Station with Telegram bot, NGRock and Grafana for Raspberry Pi

Python code for Raspberry Pi (Used on Raspberry Pi Zero W), using mostly Adafruit parts.
Inside the code you will find that:
- It uses telegram bots to get access to you data.
- Grafana to display data.
- It uses NGRock to create a tunnel to access your dashboard remotety.
- It will place a startup script to autostart your but script and your data collection.

## Bot token
You are going to need a token from the BotFather to use this code (https://telegram.me/BotFather)

## NGRock token
You are going to need a token from NGrock to use this code (https://ngrok.com/)

## Python config

Version: python 3.6
[Python modules](config_files/requirements.txt)

## Before starting
- Git should be installed and repository in place:
```
sudo apt-get update -y
sudo apt-get install git -y
git clone https://github.com/MarvinXuya/weather_station_with_telegram_bot.git /home/pi/weather_station_with_telegram_bot
```

- Internet is required:
Wifi config: https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

- Make sure to place all require information on [config.json](config_files/config.json)

## Notes
- It will be easier to setup if ssh is enable
- Weather station code was based on [Build your own weather station by Raspberry](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station)

## Setting all in place
```
sudo bash ./config_files/install.sh <Replace with your bot name>
```

## Parts of Weather station

Most of the parts were bought at Amazon:
- [WeatherRack - Anemometer / Wind Vane / Rain Bucket designed for SwitchDoc Labs WeatherPiArduino Board and Raspberry Pi/Arduino](https://www.amazon.com/dp/B00QURVHN6/ref=cm_sw_em_r_mt_dp_U_WzojEbJCR405C)
by SwitchDoc Labs

- [Adafruit MCP3008 8-Channel 10-Bit ADC With SPI Interface for Raspberry Pi](https://www.amazon.com/dp/B00NAY3RB2/ref=cm_sw_em_r_mt_dp_U_.AojEb42GG8CE)
by 3DMakerWorld, Inc.

- [Waveshare BME280 Environmental Sensor, Temperature, Humidity, Barometric Pressure Detection Module I2C/SPI Interface for Weather Forecast, IoT Projects, ect](https://www.amazon.com/dp/B07P4CWGGK/ref=cm_sw_em_r_mt_dp_U_2BojEb9E1VDMY)
by Coolwell Technology

- [RJ11 6P6C Connector Breakout Board Module RA Screw terminals](https://www.amazon.com/dp/B077YCJDPP/ref=cm_sw_em_r_mt_dp_U_5DojEbQFEMPXZ)
by MDFLY, INC
