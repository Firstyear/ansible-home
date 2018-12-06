FROM opensuse/tumbleweed:latest
MAINTAINER william@blackhats.net.au

EXPOSE 3128

# /usr/bin/docker run --restart always -v squid_log:/var/log -v squid_cache:/var/spool/squid -p 3128:3128 --name squid registry.blackhats.net.au/squid

RUN zypper install -y squid timezone && \
    zypper clean

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

COPY squid.conf /etc/squid/squid.conf

## WARNING: Need to make log folders dynamic.
# COPY squid-log.conf /etc/tmpfiles.d/squid-log.conf
# RUN systemctl enable squid.service

# ENV container docker
# STOPSIGNAL SIGRTMIN+3
COPY squid-runner.sh /root/squid-runner.sh
RUN chmod +x /root/squid-runner.sh

CMD [ "/root/squid-runner.sh" ]

