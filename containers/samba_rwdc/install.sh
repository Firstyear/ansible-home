#/bin/bash

NAME=${NAME:=samba_rwdc}
IMAGE=${IMAGE:=registry.blackhats.net.au/samba_rwdc}

# Make sure our paths exist
mkdir -p /host/var/lib/${NAME}
# ExecStart=/usr/bin/docker run --rm -v /var/samba/etc:/usr/local/samba/etc/samba -v /var/samba/var:/usr/local/samba/var -v /var/samba/private:/usr/local/samba/private -p 53:53 -p 53:53/udp -p 135:135 -p 139:139 -p 389:389 -p 389:389/udp -p 464:464 -p 464:464/udp -p 88:88 -p 88:88/udp -p 636:636 -p 445:445 -p 3268:3268 -p 3269:3269 --name=${NAME} ${IMAGE}

cat > /host/etc/systemd/system/${NAME}.service << DEVEOF
[Unit]
Description=${NAME}
After=docker.service
Requires=docker.service

[Service]
ExecStartPre=-/usr/bin/docker rm ${NAME}
ExecStart=/usr/bin/docker run --rm -v /var/lib/samba/var:/usr/local/samba/var --network=host --name=${NAME} ${IMAGE}
ExecStop=/usr/bin/docker stop -t 60 ${NAME}

[Install]
WantedBy=multi-user.target

DEVEOF
cat /host/etc/systemd/system/${NAME}.service

chroot "/host" /usr/bin/systemctl daemon-reload
chroot "/host" /usr/bin/systemctl enable "${NAME}.service"

# EXPOSE 

