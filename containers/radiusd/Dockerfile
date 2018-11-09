FROM centos:7
MAINTAINER william@blackhats.net.au

EXPOSE 1812 1813

LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="radiusd"

RUN echo HTTP_PROXY="http://proxy-bne1.net.blackhats.net.au:3128" > /etc/sysconfig/proxy

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

RUN yum install -y freeradius freeradius-utils freeradius-ldap openldap-clients && \
    yum clean all && \
    rpm --rebuilddb

# Deploy the radiusd configs. We have to copy each file to overwrite all the
# provided/shipped configs.
COPY files/raddb/mods-available/eap /etc/raddb/mods-available/eap
COPY files/raddb/mods-available/ldap /etc/raddb/mods-available/ldap
COPY files/raddb/sites-available/check-eap-tls /etc/raddb/sites-available/check-eap-tls
COPY files/raddb/sites-available/default /etc/raddb/sites-available/default
COPY files/raddb/sites-available/inner-tunnel /etc/raddb/sites-available/inner-tunnel
COPY files/raddb/clients.conf /etc/raddb/clients.conf
COPY files/raddb/radiusd.conf /etc/raddb/radiusd.conf

# Symlink in available sites and mods.
RUN ln -s ..//mods-available/ldap /etc/raddb/mods-enabled/ldap && \
    ln -s ../sites-available/check-eap-tls /etc/raddb/sites-enabled/check-eap-tls && \
    chown -R root:radiusd /etc/raddb

RUN mkdir -p /etc/systemd/system/radiusd.service.d
COPY radiusd.conf /etc/systemd/system/radiusd.service.d/local.conf
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
# Fix the raddb perms
RUN chown root:root /etc/pki/tls/certs/bh_ldap.crt && \
    chmod 644 /etc/pki/tls/certs/bh_ldap.crt && \
    chown root:root /etc/systemd/system/radiusd.service.d/local.conf

RUN systemctl enable radiusd.service

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]

