# get bme280

import bme280
import smbus2


def get_bme280():
    port = 1
    address = 0x77
    try:
        bus = smbus2.SMBus(port)
        bme280.load_calibration_params(bus, address)
        bme280_data = bme280.sample(bus, address)
        message = ("\nHumidity: " + str(round(bme280_data.humidity, 2)) + "%"
                   + "\nPresure: " + str(round(bme280_data.pressure, 2))
                   + "\nTemperature BME280: "
                   + str(round(bme280_data.temperature, 2)) + "C")
        if 'bus' in locals():
            bus.close()
        return message
    except Exception:
        if 'bus' in locals():
            bus.close()
