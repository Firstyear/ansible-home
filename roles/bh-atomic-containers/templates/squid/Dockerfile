FROM centos:7
MAINTAINER wibrown@redhat.com

EXPOSE 3128

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

RUN yum upgrade -y && \
    yum install -y squid && \
    yum clean all && \
    rpm --rebuilddb

COPY squid.conf /etc/squid/squid.conf

## WARNING: Need to make log folders dynamic.
COPY squid-log.conf /etc/tmpfiles.d/squid-log.conf
RUN systemctl enable squid.service

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]

