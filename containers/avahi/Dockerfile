FROM opensuse/tumbleweed:latest
LABEL mantainer william@blackhats.net.au

RUN zypper ar obs://home:firstyear:kanidm home_firstyear_kanidm && \
    zypper --gpg-auto-import-keys ref --force && \
    zypper install -y \
        avahi avahi-utils iproute2 && \
    zypper clean -a

CMD ["/usr/sbin/avahi-daemon", "--no-drop-root"]

