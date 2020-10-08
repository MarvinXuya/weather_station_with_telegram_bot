import board
import busio
import adafruit_si7021


def get_si7021():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_si7021.SI7021(i2c)
    message = ("\nTemperature SI7021: %0.1f C" % sensor.temperature
               + "\nHumidity: %0.1f %%" % sensor.relative_humidity)
    return message
