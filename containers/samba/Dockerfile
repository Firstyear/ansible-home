FROM centos:7
MAINTAINER william@blackhats.net.au

EXPOSE 445

#### Remember to domain join with net ads join -S dc_name -U administrator

LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="samba"

RUN echo HTTP_PROXY="http://proxy-bne1.net.blackhats.net.au:3128" > /etc/sysconfig/proxy

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

# Need nfs-utils to resolve nfs-nobody

RUN yum install -y samba sssd openldap-clients sssd-ldap nfs-utils tdb-tools krb5-workstation && \
    yum clean all && \
    rpm --rebuilddb

COPY smb.conf /etc/samba/smb.conf

# You can add the passwords via passdb.tdb

COPY sssd-log.conf /etc/tmpfiles.d/sssd-log.conf
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
COPY nsswitch.conf /etc/nsswitch.conf
COPY sssd.conf /etc/sssd/sssd.conf
RUN chown root:root /etc/sssd/sssd.conf && \
    chown root:root /etc/nsswitch.conf && \
    chown root:root /etc/pki/tls/certs/bh_ldap.crt && \
    chmod 600 /etc/sssd/sssd.conf

RUN systemctl enable smb.service && \
    systemctl enable sssd

RUN mkdir -p /data

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]
