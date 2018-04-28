FROM centos:7
MAINTAINER william@blackhats.net.au

EXPOSE 21 30000 30001 30002 30003 30004 30005 30006 30007 30008 30009

LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="vsftpd"

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

# Need nfs-utils to resolve nfs-nobody

RUN yum upgrade -y && \
    yum install -y vsftpd sssd openldap-clients sssd-ldap nfs-utils && \
    yum clean all && \
    rpm --rebuilddb

COPY vsftpd.conf /etc/vsftpd/vsftpd.conf
COPY sssd-log.conf /etc/tmpfiles.d/sssd-log.conf
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
COPY nsswitch.conf /etc/nsswitch.conf
COPY sssd.conf /etc/sssd/sssd.conf
RUN chown root:root /etc/sssd/sssd.conf && \
    chown root:root /etc/nsswitch.conf && \
    chown root:root /etc/pki/tls/certs/bh_ldap.crt && \
    chmod 600 /etc/sssd/sssd.conf && \
    chmod 600 /etc/vsftpd/vsftpd.conf

RUN systemctl enable vsftpd.service && \
    systemctl enable sssd.service

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]

