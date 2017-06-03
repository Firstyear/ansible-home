FROM centos:7
MAINTAINER wibrown@redhat.com

EXPOSE 80 443

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

RUN yum upgrade -y && \
    yum install -y epel-release && \
    yum install -y nextcloud nextcloud-sqlite nextcloud-httpd mod_ssl && \
    yum clean all && \
    rpm --rebuilddb

# This is to allow LDAP to work
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
COPY ldap.conf /etc/openldap/ldap.conf

COPY ssl.conf /etc/httpd/conf.d/ssl.conf
# This makes the service available outside of localhost
RUN ln -s /etc/httpd/conf.d/nextcloud-access.conf.avail /etc/httpd/conf.d/z-nextcloud-access.conf

RUN systemctl enable httpd.service

# volume /var/lib/nextcloud/data
# volume for /etc/nextcloud too!!!

# How do I inject TLS?

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]




