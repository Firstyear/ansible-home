FROM fedora:27
MAINTAINER william@blackhats.net.au

EXPOSE 53 53/udp 135 139 389 389/udp 464 464/udp 88 88/udp 636 445 3268 3269

LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="samba_rwdc"

RUN echo HTTP_PROXY="http://proxy-bne1.net.blackhats.net.au:3128" > /etc/sysconfig/proxy

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

# Need nfs-utils to resolve nfs-nobody

RUN dnf upgrade -y && \
    dnf install -y attr bind-utils docbook-style-xsl gcc gdb krb5-workstation \
       libsemanage-python libxslt perl perl-ExtUtils-MakeMaker \
       perl-Parse-Yapp perl-Test-Base pkgconfig policycoreutils-python \
       python-crypto gnutls-devel gpgme-devel jansson-devel libattr-devel \
       keyutils-libs-devel libacl-devel libaio-devel libblkid-devel \
       libxml2-devel openldap-devel pam-devel popt-devel python2-devel \
       readline-devel systemd-devel zlib-devel python-markdown \
    sssd openldap-clients sssd-ldap tdb-tools bind && \
    dnf clean all

RUN mkdir -p /usr/local/src
WORKDIR /usr/local/src
RUN rm /etc/krb5.conf

COPY named.conf /etc/named.conf
RUN chown root:named /etc/named.conf && \
    chmod 640 /etc/named.conf

ADD https://download.samba.org/pub/samba/stable/samba-4.8.2.tar.gz /usr/local/src/
RUN tar -xvf samba-4.8.2.tar.gz
WORKDIR /usr/local/src/samba-4.8.2
RUN ./configure.developer --with-systemd --enable-debug --enable-developer \
    --sysconfdir=/usr/local/samba/var/etc --with-privatedir=/usr/local/samba/var/private \
    --with-bind-dns-dir=/usr/local/samba/var/bind-dns && \
    make && \
    make install && \
    cp /usr/local/src/samba-4.8.2/bin/default/packaging/systemd/samba.service /etc/systemd/system/

# COPY sssd-log.conf /etc/tmpfiles.d/sssd-log.conf
# COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
# COPY nsswitch.conf /etc/nsswitch.conf
# COPY sssd.conf /etc/sssd/sssd.conf
# RUN chown root:root /etc/sssd/sssd.conf && \
#     chown root:root /etc/nsswitch.conf && \
#     chown root:root /etc/pki/tls/certs/bh_ldap.crt && \
#     chmod 600 /etc/sssd/sssd.conf

# Setup the alias for samba to access bind dns
# WORKDIR /usr/local/samba
# RUN rm -r /usr/local/samba/bind-dns && \
#     ln -s ln -s var/bind-dns bind-dns

RUN systemctl enable samba.service && \
    systemctl enable sssd.service && \
    systemctl enable named.service

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]

