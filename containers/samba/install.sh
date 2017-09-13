#/bin/bash

NAME=${NAME:=samba}
IMAGE=${IMAGE:=registry.blackhats.net.au/samba}

# Make sure our paths exist
mkdir -p /host/var/lib/${NAME}

cat > /host/etc/systemd/system/${NAME}.service << DEVEOF
[Unit]
Description=${NAME}
After=docker.service
Requires=docker.service

[Service]
ExecStartPre=-/usr/bin/docker rm ${NAME}
ExecStart=/usr/bin/docker run --rm -v /var/lib/${NAME}/data:/data -v /var/lib/${NAME}/data/home:/home -v /var/lib/${NAME}/private:/var/lib/samba/private -p 445:445 --name=${NAME} ${IMAGE}
ExecStop=/usr/bin/docker stop -t 60 ${NAME}

[Install]
WantedBy=multi-user.target

DEVEOF
cat /host/etc/systemd/system/${NAME}.service

chroot "/host" /usr/bin/systemctl daemon-reload
chroot "/host" /usr/bin/systemctl enable "${NAME}.service"


