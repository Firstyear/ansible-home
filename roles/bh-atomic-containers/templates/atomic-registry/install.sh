#/bin/sh

NAME=${NAME:=atomic-registry}
IMAGE=${IMAGE:=atomic-registry}
PORT=${PORT:=-p 443:443}
OPTIONS=${OPTIONS:=-e REGISTRY_HTTP_ADDR=0.0.0.0:443 -e REGISTRY_HTTP_TLS_CERTIFICATE=/var/lib/registry/certs/docker.crt -e REGISTRY_HTTP_TLS_KEY=/var/lib/registry/certs/docker.key -e REGISTRY_HTTP_TLS_CLIENTCAS=[/var/lib/registry/certs/ca.crt]  }

# Make sure our paths exist
mkdir -p /var/lib/${NAME}

cat > /host/etc/systemd/system/${NAME}.service << DEVEOF
[Unit]
Description=${NAME}
After=docker.service
Requires=docker.service

[Service]
ExecStartPre=-/usr/bin/docker rm ${NAME}
ExecStart=/usr/bin/docker run --rm -v /var/lib/${NAME}:/var/lib/registry ${OPTIONS} ${PORT} --name=${NAME} ${IMAGE}
ExecStop=/usr/bin/docker stop -t 60 ${NAME}

[Install]
WantedBy=multi-user.target

DEVEOF
cat /host/etc/systemd/system/${NAME}.service

chroot "/host" /usr/bin/systemctl daemon-reload
chroot "/host" /usr/bin/systemctl enable "${NAME}.service"


