#!/bin/bash

### BEGIN INIT INFO
# Provides:          weatherstation
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Starts mysql script and weather station script
# Description:       Only start option is available at startup.
### END INIT INFO


# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Shutting lights out"
    echo none | sudo tee /sys/class/leds/led0/trigger
    echo 1 | sudo tee /sys/class/leds/led0/brightness
    cd /home/pi/weather_station_with_telegram_bot/weatherbot
    while !(sudo mysqladmin ping)
    do
       sleep 3
       echo "waiting for mysql ..."
    done
    echo "Starting Bot for telegram"
    nohup sudo python3 weatherbot.py &
    echo "Starting mysql script for weather station"
    nohup python3 weather_shadow.py &
    ;;
  *)
    echo "Usage: /etc/init.d/startup.sh {start}"
    exit 1
    ;;
esac

exit 0
