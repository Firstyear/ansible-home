FROM centos:7
MAINTAINER wibrown@redhat.com

EXPOSE 1812 1813

LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="radiusd"

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

# Need nfs-utils to resolve nfs-nobody

RUN yum upgrade -y && \
    yum install -y freeradius freeradius-utils freeradius-ldap && \
    yum clean all && \
    rpm --rebuilddb

COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
RUN chown root:root /etc/pki/tls/certs/bh_ldap.crt

RUN systemctl enable radiusd.service

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]

