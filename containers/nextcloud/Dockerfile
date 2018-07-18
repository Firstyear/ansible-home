FROM centos:7
MAINTAINER william@blackhats.net.au

EXPOSE 80 443

LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="nextcloud"

RUN echo HTTP_PROXY="http://proxy-bne1.net.blackhats.net.au:3128" > /etc/sysconfig/proxy

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

# Sudo is used for occ admin cli tasks

RUN yum upgrade -y && \
    yum install -y epel-release && \
    yum install -y nextcloud nextcloud-sqlite nextcloud-httpd mod_ssl sudo redis php-pecl-redis && \
    yum clean all && \
    rpm --rebuilddb

# This is to allow LDAP to work
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
COPY ldap.conf /etc/openldap/ldap.conf

COPY ssl.conf /etc/httpd/conf.d/ssl.conf
COPY nextcloud.ini /etc/php.d/nextcloud.ini
# This makes the service available outside of localhost
RUN ln -s /etc/httpd/conf.d/nextcloud-access.conf.avail /etc/httpd/conf.d/z-nextcloud-access.conf

RUN systemctl enable redis.service && \
    systemctl enable httpd.service

# volume /var/lib/nextcloud/data
# volume for /etc/nextcloud too!!!

# How do I inject TLS?

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]




