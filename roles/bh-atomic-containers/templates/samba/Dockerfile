FROM centos:7
MAINTAINER wibrown@redhat.com

EXPOSE 445

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

# Need nfs-utils to resolve nfs-nobody

RUN yum upgrade -y && \
    yum install -y samba sssd openldap-clients sssd-ldap nfs-utils && \
    yum clean all && \
    rpm --rebuilddb

COPY smb.conf /etc/samba/smb.conf

# You can add the passwords via passdb.tdb

COPY sssd-log.conf /etc/tmpfiles.d/sssd-log.conf
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
COPY nsswitch.conf /etc/nsswitch.conf
COPY sssd.conf /etc/sssd/sssd.conf
RUN chown root:root /etc/sssd/sssd.conf && \
    chmod 600 /etc/sssd/sssd.conf

RUN systemctl enable smb.service && \
    systemctl enable sssd

RUN mkdir -p /data && \
    rmdir /home && \
    ln -sf /home /data/home

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]
