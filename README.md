# Weather Station with telegram bot

Python code for Raspberry Pi (Raspberry Pi Zero W), using mostly Adafruit parts.

## Bot token
You are going to need a token from the BotFather to use this code (https://telegram.me/BotFather)

## Python config

Version: python 3.6
[Python modules](config_files/requirements.txt)

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

## Starting the bot

If you want to run it in background
```
nohup python3.6 weather_bot.py &
```
