FROM centos:7
MAINTAINER wibrown@redhat.com

# mount at /opt/unifi/data

LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="unifi"

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

RUN useradd unifi

RUN yum upgrade -y && \
    yum install -y epel-release && \
    yum install -y lsb wget java mongodb-server unzip && \
    yum clean all && \
    rpm --rebuilddb

COPY unifi.service /etc/systemd/system/unifi.service
COPY UniFi.unix.zip /root/UniFi.unix.zip

RUN unzip /root/UniFi.unix.zip -d /opt/ && \
    chown -R unifi: /opt/UniFi

RUN systemctl enable unifi.service

### WARNING: Remember to change the inform systemip on the system.properties

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]

