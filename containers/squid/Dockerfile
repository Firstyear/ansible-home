FROM opensuse/tumbleweed:latest
MAINTAINER william@blackhats.net.au

EXPOSE 3128

# This is the information to allow ATOMIC to install and run this.
LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -v /var/lib/\${NAME}:/var/spool/squid -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/bash /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -v /var/lib/\${NAME}:/var/spool/squid -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/bash /bin/uninstall.sh \${OPT3}"
LABEL "Name"="squid"
LABEL RUN '/usr/bin/docker run -t -i --rm \${OPT1} -v /var/log/squid:/var/log -v /var/lib/\${NAME}:/var/spool/squid -p 3128:3128 --name \${NAME} \${IMAGE} \${OPT2}'

RUN echo HTTP_PROXY="http://proxy-bne1.net.blackhats.net.au:3128" > /etc/sysconfig/proxy

COPY install.sh /bin/
COPY uninstall.sh /bin/
COPY help.sh /bin/
LABEL HELP docker run --rm \${IMAGE} /bin/bash /bin/help.sh

#RUN yum upgrade -y && \
#    yum install -y squid && \
#    yum clean all && \
#    rpm --rebuilddb

RUN zypper install -y squid timezone && \
    zypper clean

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

COPY squid.conf /etc/squid/squid.conf

## WARNING: Need to make log folders dynamic.
COPY squid-log.conf /etc/tmpfiles.d/squid-log.conf
RUN systemctl enable squid.service

ENV container docker
STOPSIGNAL SIGRTMIN+3
CMD [ "/sbin/init" ]

