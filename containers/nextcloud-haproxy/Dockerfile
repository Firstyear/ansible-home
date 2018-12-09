FROM opensuse/tumbleweed:latest
MAINTAINER william@blackhats.net.au

EXPOSE 443

# /usr/bin/docker run --restart always -v /etc/letsencrypt:/etc/letsencrypt -p 443:443 --name nextcloud-haproxy registry.blackhats.net.au/nextcloud-haproxy

RUN zypper install -y haproxy timezone && \
    zypper clean

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

COPY haproxy.cfg /etc/haproxy/haproxy.cfg

CMD [ "/usr/sbin/haproxy", "-f", "/etc/haproxy/haproxy.cfg", "-db" ]

