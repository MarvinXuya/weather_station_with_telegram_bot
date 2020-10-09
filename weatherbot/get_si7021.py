import board
import busio
import adafruit_si7021


def get_si7021():
    i2c = busio.I2C(board.SCL, board.SDA)
    while True:
        try:
            sensor = adafruit_si7021.SI7021(i2c)
            break
        except OSError:
            continue
    return sensor
