#!/bin/bash

bot_name=${1}
timedatectl_country=${timedatectl_country:-America/Guatemala}
grafana_version=${grafana_version:-7.2.2}
if [ -z $bot_name ] ; then
  echo "Bot name is needed.
  Usage: ./install.sh <bot name>"
  exit 1
fi


# Set the right timezone on your raspberry for mariadb
echo "Setting time zone for ${timedatectl_country}"
timedatectl set-timezone ${timedatectl_country}

echo "Installing packages"
sudo apt-get update
sudo apt-get install -y python3.6 python3-pip python3-distutils mariadb-server mariadb-client libmariadbclient-dev adduser libfontconfig1 i2c-tools

sudo apt --fix-broken install -y
sudo apt-get install -y python3-testresources
curl https://bootstrap.pypa.io/get-pip.py | python3
sudo python3 -m pip install -r /home/pi/weather_station_with_telegram_bot/requirements.txt

echo "Setting log rotate"
sudo cp /home/pi/weather_station_with_telegram_bot/data/bot_name.conf /etc/logrotate.d/${bot_name}
sudo sed -i "s/<bot_name>/${bot_name}/g" /etc/logrotate.d/${bot_name}
chmod 544 /etc/logrotate.d/${bot_name}

echo "Settup for grafana"
wget https://dl.grafana.com/oss/release/grafana-rpi_${grafana_version}_armhf.deb
sudo dpkg -i grafana-rpi_${grafana_version}_armhf.deb
sleep 30
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

sudo cp /home/pi/weather_station_with_telegram_bot/config_files/startup.sh /etc/init.d/startup.sh
sudo chmod 755 /etc/init.d/startup.sh
sudo update-rc.d -f startup.sh defaults

sudo echo w1-gpio >> /etc/modules
sudo echo w1-therm >> /etc/modules

if ! grep dtoverlay=w1-gpio /boot/config.txt ; then
  sudo echo dtoverlay=w1-gpio >> /boot/config.txt
fi

if ! grep i2c_arm=on < /boot/config.txt ; then
  echo "Adding i2c"
  sudo echo "dtparam=i2c_arm=on" >> /boot/config.txt
fi

echo "Adding mysql setup"
sudo cat >> /etc/mysql/mariadb.cnf << block
[mysqld]
port = 3306
user = ${bot_name}
bind-address = 0.0.0.0
block
sudo systemctl restart mysql
