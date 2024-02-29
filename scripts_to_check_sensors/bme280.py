import board
import busio
import adafruit_bme280
from time import sleep
while True:
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        bme280data = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        print("\nHumidity: "
              + str(round(bme280data.humidity, 2))
              + "%"
              + "\nPresure: "
              + str(round(bme280data.pressure, 2))
              + "\nTemperature BME280: "
              + str(round(bme280data.temperature, 2)) + "C")
        sleep (5)
    except Exception:
        print('Not able to get data, make sure bme280 is connected')
