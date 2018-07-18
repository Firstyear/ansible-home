FROM centos:7
MAINTAINER wibrown@redhat.com

EXPOSE 10080

# Test deployment

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

RUN yum upgrade -y && \
    yum install -y which openssl amanda-client "/sbin/init" && \
    yum clean all && \
    rpm --rebuilddb

COPY amandahosts /var/lib/amanda/.amandahosts
COPY backup-pubkey.pem /var/lib/amanda/backup-pubkey.pem
COPY amanda-log.conf /etc/tmpfiles.d/amanda-log.conf
COPY exclude /var/lib/amanda/exclude
RUN chown amandabackup:disk /var/lib/amanda/{.amandahosts,backup-pubkey.pem,exclude} && \
    chmod 600 /var/lib/amanda/{.amandahosts,backup-pubkey.pem,exclude}

RUN systemctl enable amanda.socket

# Have to make this in the image, not in a systemd controlled location.
RUN mkdir /sysroot

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]


