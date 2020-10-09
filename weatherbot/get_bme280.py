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
        if 'bus' in locals():
            bus.close()
        return bme280_data
    except Exception:
        if 'bus' in locals():
            bus.close()
