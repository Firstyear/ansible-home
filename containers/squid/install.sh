#/bin/bash

NAME=${NAME:=squid}
IMAGE=${IMAGE:=registry.blackhats.net.au/squid}
LOGDIR=${LOGDIR:=/var/log/squid}

# Make sure our paths exist
mkdir -p /host/${LOGDIR}
mkdir -p /host/var/lib/${NAME}

chown -R 23:23 /var/lib/${NAME}

cat > /host/etc/systemd/system/${NAME}.service << DEVEOF
[Unit]
Description=${NAME}
After=docker.service
Requires=docker.service

[Service]
ExecStartPre=-/usr/bin/docker rm ${NAME}
ExecStart=/usr/bin/docker run --rm -v ${LOGDIR}:/var/log -v /var/lib/${NAME}:/var/spool/squid -p 3128:3128 --name=${NAME} ${IMAGE}
ExecStop=/usr/bin/docker stop -t 60 ${NAME}

[Install]
WantedBy=multi-user.target

DEVEOF
cat /host/etc/systemd/system/${NAME}.service

chroot "/host" /usr/bin/systemctl daemon-reload
chroot "/host" /usr/bin/systemctl enable "${NAME}.service"


