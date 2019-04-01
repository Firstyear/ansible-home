# FROM opensuse/leap:latest
FROM opensuse/tumbleweed:latest
MAINTAINER william@blackhats.net.au

EXPOSE 389 636 3268 3269

# docker create -v samba_rwdc:/var/lib/samba --network=host --name=samba_rwdc registry.blackhats.net.au/samba_rwdc

RUN echo HTTP_PROXY="http://proxy-bne1.net.blackhats.net.au:3128" > /etc/sysconfig/proxy

RUN zypper install -y iproute2 procps openldap2-client samba-ad-dc timezone && \
    zypper clean

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

# Setup our config ...

# COPY smb.conf /etc/samba/smb.conf
RUN ln -sf /var/lib/samba/smb.conf /etc/samba/smb.conf

ENV container docker
CMD [ "/usr/sbin/samba", "--foreground", "--no-process-group" ]

