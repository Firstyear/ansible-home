FROM fedora:27
MAINTAINER william@blackhats.net.au


LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="nextcloud"

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
RUN cd /etc && ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

RUN dnf upgrade -y && \
    dnf install -y python3-devel gcc && \
    pip3 install lifxlan && \
    dnf clean all

COPY lifxctl.py /home/lifx/lifxctl.py

# You can't use this because LOL DOCKER ATOMIC needs ROOT to install haha.
# RUN useradd -m -r lifx
# USER lifx
ENV container docker
# STOPSIGNAL SIGRTMIN+3
CMD [ "/usr/bin/python3", "/home/lifx/lifxctl.py" ]
