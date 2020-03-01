#!/bin/bash

bot_name=${1}

sudo apt-get update
sudo apt-get install -y python3.6
sudo apt-get install -y python3-pip
sudo apt-get install -y mariadb-server mariadb-client libmariadbclient-dev
sudo pip3 install /home/pi/weather_station_with_telegram_bot/config_files/requirements.txt

sudo cp /home/pi/weather_station_with_telegram_bot/templates/bot_name.conf /etc/logrotate.d/${bot_name}
sed -i "s/<bot_name>/${bot_name}/g" /etc/logrotate.d/${bot_name}
chmod 544 /etc/logrotate.d/${bot_name}

wget https://dl.grafana.com/oss/release/grafana-rpi_6.6.1_armhf.deb
sudo dpkg -i grafana-rpi_6.6.1_armhf.deb
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

sudo cp /home/pi/weather_station_with_telegram_bot/templates/startup.sh /etc/logrotate.d/startup.sh
sudo chmod 755 /etc/init.d/startup.sh
sudo update-rc.d -f startup.sh defaults
