#/bin/bash

NAME=${NAME:=nextcloud}
IMAGE=${IMAGE:=registry.blackhats.net.au/nextcloud}

# Make sure our paths exist
mkdir -p /host/var/lib/${NAME}

cat > /host/etc/systemd/system/${NAME}.service << DEVEOF
[Unit]
Description=${NAME}
After=docker.service
Requires=docker.service

[Service]
ExecStartPre=-/usr/bin/docker rm ${NAME}
ExecStart=/usr/bin/docker run --rm -v /var/lib/${NAME}/data:/var/lib/nextcloud/data -v /var/lib/${NAME}/config:/etc/nextcloud -p 80:80 -p 443:443 --name=${NAME} ${IMAGE}
ExecStop=/usr/bin/docker stop -t 60 ${NAME}

[Install]
WantedBy=multi-user.target

DEVEOF
cat /host/etc/systemd/system/${NAME}.service

chroot "/host" /usr/bin/systemctl daemon-reload
chroot "/host" /usr/bin/systemctl enable "${NAME}.service"


