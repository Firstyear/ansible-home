#/bin/bash

NAME=${NAME:=radiusd}
IMAGE=${IMAGE:=registry.blackhats.net.au/radiusd}

# Make sure our paths exist
mkdir -p /host/var/lib/${NAME}/pki
# ExecStart=/usr/bin/docker run --rm -v /etc/${NAME}:/etc/raddb -p 1812:1812 -p 1813:1813 --name=${NAME} ${IMAGE}

cat > /host/etc/systemd/system/${NAME}.service << DEVEOF
[Unit]
Description=${NAME}
After=docker.service
Requires=docker.service

[Service]
ExecStartPre=-/usr/bin/docker rm ${NAME}
ExecStart=/usr/bin/docker run --rm -v /var/lib/${NAME}/pki:/etc/pki/radius --network=host --name=${NAME} ${IMAGE}
ExecStop=/usr/bin/docker stop -t 60 ${NAME}

[Install]
WantedBy=multi-user.target

DEVEOF
cat /host/etc/systemd/system/${NAME}.service

chroot "/host" /usr/bin/systemctl daemon-reload
chroot "/host" /usr/bin/systemctl enable "${NAME}.service"



