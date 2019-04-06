FROM opensuse/leap:latest
MAINTAINER william@blackhats.net.au

EXPOSE 1812 1813

# docker run --rm -i -t -p 1812:1812 -p 1812:1812/udp -p 1813:1813 -p 1813:1813/udp -v radiusd_pki:/etc/pki/radius registry.blackhats.net.au/radiusd:latest
#    /usr/sbin/radiusd -X
# docker create -i -t --restart always -p 1812:1812 -p 1812:1812/udp -p 1813:1813 -p 1813:1813/udp -v radiusd_pki:/etc/pki/radius --name radiusd registry.blackhats.net.au/radiusd:latest


RUN zypper install -y timezone freeradius-client freeradius-server freeradius-server-ldap \
    freeradius-server-python openldap2-client freeradius-server-utils \
    python2 && \
    zypper clean

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

# Deploy the radiusd configs. We have to copy each file to overwrite all the
# provided/shipped configs.
COPY files/raddb/mods-available/eap /etc/raddb/mods-available/eap
COPY files/raddb/mods-available/python /etc/raddb/mods-available/python

# The possible "tunnels" that will be taken, usually mschapv2
COPY files/raddb/sites-available/default /etc/raddb/sites-available/default
COPY files/raddb/sites-available/inner-tunnel /etc/raddb/sites-available/inner-tunnel

# Defines our NAS
COPY files/raddb/clients.conf /etc/raddb/clients.conf
# Defines site local var
COPY files/raddb/radiusd.conf /etc/raddb/radiusd.conf

COPY test.py /etc/raddb/test.py

# Symlink in available sites and mods.
RUN ln -s ../mods-available/python /etc/raddb/mods-enabled/python && \
    chown -R root:radiusd /etc/raddb

RUN mkdir -p /etc/pki/tls/certs/
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
# Fix the raddb perms
RUN chown root:root /etc/pki/tls/certs/bh_ldap.crt && \
    chmod 644 /etc/pki/tls/certs/bh_ldap.crt


USER radiusd
CMD [ "/usr/sbin/radiusd", "-f", "-l", "stdout" ]

