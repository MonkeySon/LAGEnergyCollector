#!/usr/bin/env bash

set -e

INSTALL_DIR="/opt/LAGEnergyCollector/"

echo "=== Installing LAGEnergyCollector application ==="

read -p "Enter install directory [$INSTALL_DIR]: " NEW_INSTALL_DIR

if [[ ! -z $NEW_INSTALL_DIR ]]; then
    INSTALL_DIR=$(echo "$NEW_INSTALL_DIR/" | tr -s /)
fi

if [[ ! -d $INSTALL_DIR ]]; then
    echo "Creating directory $INSTALL_DIR ..."
    mkdir -p $INSTALL_DIR
fi

echo "Copying over files ..."
cp -f src/*.py $INSTALL_DIR

if [[ -f ${INSTALL_DIR}config.json ]]; then
    read -p "Configuration already exists! Create backup and overwrite? y/[n]: " OVERWRITE_CONFIG
    if [[ $OVERWRITE_CONFIG == "y" ]]; then
        echo "Backing up and overwriting config ..."
        cp -f ${INSTALL_DIR}config.json ${INSTALL_DIR}config.json.backup
        cp -f src/config.json $INSTALL_DIR
    fi
else
    cp -f src/config.json $INSTALL_DIR
fi

chmod o-r ${INSTALL_DIR}*

echo "=== Installing LAGEnergyCollector systemd service ==="

echo "Copying over service and timer ..."

cp -f systemd/* /etc/systemd/system/

echo "Setting correct path in system ..."

sed -i "s|{WORKDIR}|${INSTALL_DIR}|g" /etc/systemd/system/linzag-energy-collector.service

echo "Enabling service timer ..."

systemctl enable linzag-energy-collector.timer
systemctl start linzag-energy-collector.timer

echo "=== Done ==="