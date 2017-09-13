#/bin/bash

NAME=${NAME:=unifi}

chroot "/host" /usr/bin/systemctl disable "${NAME}.service"
chroot "/host" /usr/bin/systemctl stop "${NAME}.service"
rm -f "/host/etc/systemd/system/${NAME}.service"


