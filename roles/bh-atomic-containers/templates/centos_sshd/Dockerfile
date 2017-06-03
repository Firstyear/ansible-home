FROM centos:7
MAINTAINER wibrown@redhat.com

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

# If centos / el7, we need to build the locale

# You may need to install glibc-locale-source because f26 is fucked

RUN /usr/bin/yum install -y glibc-locale-source epel-release

RUN localedef -i en_AU -c -f UTF-8 en_AU.UTF-8

RUN /usr/bin/yum upgrade -y && \
    /usr/bin/yum install -y redhat-rpm-config sssd openldap-clients sssd-ldap \
    sudo vim screen git make iproute iputils findutils zsh strace ldapvi \
    procps-ng bind-utils yum-utils nc openssh-server && \
    /usr/bin/yum clean all && rpm --rebuilddb

COPY ldap.conf /etc/openldap/ldap.conf
COPY sssd-log.conf /etc/tmpfiles.d/sssd-log.conf
COPY bh_admins-sudo /etc/sudoers.d/bh_admins-sudo
COPY bh_ldap.crt /etc/pki/tls/certs/bh_ldap.crt
COPY nsswitch.conf /etc/nsswitch.conf
COPY password-auth-ac /etc/pam.d/password-auth-ac
COPY password-auth-ac /etc/pam.d/password-auth
COPY system-auth-ac /etc/pam.d/system-auth-ac
COPY system-auth-ac /etc/pam.d/system-auth
COPY sshd_config /etc/ssh/sshd_config
COPY sssd.conf /etc/sssd/sssd.conf
RUN chown root:root /etc/sssd/sssd.conf && \
    chmod 600 /etc/sssd/sssd.conf && \
    chmod 644 /etc/nsswitch.conf

RUN systemctl enable sshd && \
    systemctl enable sssd

VOLUME /home

## `SYSTEMD.M4'
ENV container docker
STOPSIGNAL SIGRTMIN+3
EXPOSE 22
CMD [ "/sbin/init" ]

