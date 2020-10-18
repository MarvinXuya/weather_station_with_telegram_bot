# get bme280

import board
import busio
import adafruit_bme280


def get_bme280():
    while True:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
        except OSError:
            continue
        try:
            bme280_data = adafruit_bme280.Adafruit_BME280_I2C(i2c)
            break
        except OSError:
            continue
    return bme280_data
