# docker build -t firstyear/dns64:latest .

FROM opensuse/leap:latest
LABEL mantainer william@blackhats.net.au
EXPOSE 53 53/udp

RUN zypper ref && \
    zypper install -y \
        bind-utils bind && \
    zypper clean -a

VOLUME /var/lib/named/slave/

CMD ["named", "-c", "/etc/named.conf", "-g", "-u", "named"]


