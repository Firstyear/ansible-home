#/bin/bash

NAME=${NAME:=lifx}
IMAGE=${IMAGE:=registry.blackhats.net.au/lifx}

cat > /host/etc/systemd/system/${NAME}.service << DEVEOF
[Unit]
Description=${NAME}
After=docker.service
Requires=docker.service

[Service]
ExecStartPre=-/usr/bin/docker rm ${NAME}
ExecStart=/usr/bin/docker run --rm --network=host --name=${NAME} ${IMAGE}
ExecStop=/usr/bin/docker stop -t 60 ${NAME}

[Install]
WantedBy=multi-user.target

DEVEOF

cat /host/etc/systemd/system/${NAME}.service

chroot "/host" /usr/bin/systemctl daemon-reload
chroot "/host" /usr/bin/systemctl enable "${NAME}.service"


