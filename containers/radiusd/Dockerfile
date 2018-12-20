FROM opensuse/tumbleweed:latest
MAINTAINER william@blackhats.net.au

EXPOSE 1812 1813

# docker run --rm -i -t -p 1812:1812 -p 1812:1812/udp -p 1813:1813 -p 1813:1813/udp -v radiusd_pki:/etc/pki/radius registry.blackhats.net.au/radiusd:latest /usr/sbin/radiusd -X



RUN zypper install -y timezone freeradius-client freeradius-server freeradius-server-ldap freeradius-server-python openldap2-client freeradius-server-utils && \
    zypper clean

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

# Deploy the radiusd configs. We have to copy each file to overwrite all the
# provided/shipped configs.
COPY files/raddb/mods-available/eap /etc/raddb/mods-available/eap
COPY files/raddb/mods-available/ldap /etc/raddb/mods-available/ldap
COPY files/raddb/mods-config/files/authorize /etc/raddb/mods-config/files/authorize
COPY files/raddb/sites-available/check-eap-tls /etc/raddb/sites-available/check-eap-tls
COPY files/raddb/sites-available/default /etc/raddb/sites-available/default
COPY files/raddb/sites-available/inner-tunnel /etc/raddb/sites-available/inner-tunnel
COPY files/raddb/clients.conf /etc/raddb/clients.conf
COPY files/raddb/radiusd.conf /etc/raddb/radiusd.conf

# Symlink in available sites and mods.
RUN ln -s ../mods-available/ldap /etc/raddb/mods-enabled/ldap && \
    ln -s ../sites-available/check-eap-tls /etc/raddb/sites-enabled/check-eap-tls && \
    chown -R root:radiusd /etc/raddb

# RUN mkdir -p /etc/systemd/system/radiusd.service.d
# COPY radiusd.conf /etc/systemd/system/radiusd.service.d/local.conf
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
# Fix the raddb perms
RUN chown root:root /etc/pki/tls/certs/bh_ldap.crt && \
    chmod 644 /etc/pki/tls/certs/bh_ldap.crt
    # && \
    # chown root:root /etc/systemd/system/radiusd.service.d/local.conf

# RUN systemctl enable radiusd.service

USER radiusd
CMD [ "/usr/sbin/radiusd", "-f", "-l", "stdout" ]

