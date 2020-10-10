# get bme280

import board
import busio
import adafruit_bme280


def get_bme280():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        bme280_data = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        return bme280_data
    except Exception:
        bme280_data = 'Not able to get data'
        return bme280_data
