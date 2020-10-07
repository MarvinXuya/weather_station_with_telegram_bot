#!/bin/bash

bot_name=${1}

if [ -z $bot_name ] ; then
  echo "Bot name is needed.
  Usage: ./install.sh <bot name>"
  exit 1
fi

sudo apt-get update
sudo apt-get install -y python3.6
sudo apt-get install -y python3-pip
sudo apt-get install -y python3-distutils
sudo apt-get install -y mariadb-server mariadb-client libmariadbclient-dev
sudo apt-get install -y adduser libfontconfig1
sudo apt-get install -y i2c-tools

sudo apt --fix-broken install -y
sudo apt-get install -y python3-testresources
curl https://bootstrap.pypa.io/get-pip.py | python3
sudo python3 -m pip install -r /home/pi/weather_station_with_telegram_bot/requirements.txt

sudo cp /home/pi/weather_station_with_telegram_bot/data/bot_name.conf /etc/logrotate.d/${bot_name}
sudo sed -i "s/<bot_name>/${bot_name}/g" /etc/logrotate.d/${bot_name}
chmod 544 /etc/logrotate.d/${bot_name}

wget https://dl.grafana.com/oss/release/grafana-rpi_7.0.3_armhf.deb
wget https://dl.grafana.com/oss/release/grafana-rpi_6.6.1_armhf.deb
sudo dpkg -i grafana-rpi_6.6.1_armhf.deb
sleep 30
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

sudo cp /home/pi/weather_station_with_telegram_bot/config_files/startup.sh /etc/init.d/startup.sh
sudo chmod 755 /etc/init.d/startup.sh
sudo update-rc.d -f startup.sh defaults

sudo echo w1-gpio >> /etc/modules
sudo echo w1-therm >> /etc/modules

sudo echo dtoverlay=w1-gpio >> /boot/config.txt
