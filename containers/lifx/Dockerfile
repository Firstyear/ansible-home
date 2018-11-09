FROM opensuse/tumbleweed:latest
MAINTAINER william@blackhats.net.au

LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL "Name"="lifx"

# RUN echo HTTP_PROXY="http://proxy-bne1.net.blackhats.net.au:3128" > /etc/sysconfig/proxy

COPY install.sh /bin/
COPY uninstall.sh /bin/

# Timezones
# RUN zypper install -y python3 python3-devel python3-pip gcc timezone && \
#     pip3 install lifxlan && \
#     zypper rm -y -u gcc && \
#     zypper clean
#



RUN mkdir -p /home/lifx/

WORKDIR /home/lifx

RUN zypper install -y timezone git cargo rust rust-std gcc && \
    git clone https://github.com/Firstyear/lifx_ctl.git && \
    cd lifx_ctl && \
    cargo build --release

RUN cd /etc && \
    ln -sf ../usr/share/zoneinfo/Australia/Brisbane localtime

# COPY lifxctl.py /home/lifx/lifxctl.py

# You can't use this because LOL DOCKER ATOMIC needs ROOT to install haha.
# RUN useradd -m -r lifx
# USER lifx

ENV container docker
STOPSIGNAL SIGTERM
# CMD [ "/usr/bin/python3", "/home/lifx/lifxctl.py" ]

ENV RUST_BACKTRACE 1
CMD ["/home/lifx/lifx_ctl/target/release/lifx_ctl"]

