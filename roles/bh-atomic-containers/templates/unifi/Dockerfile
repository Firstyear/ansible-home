FROM centos:7
MAINTAINER wibrown@redhat.com


EXPOSE 8081 8080 8443 8880 8843 10001/udp 3478/udp
# mount at /opt/unifi/data

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

