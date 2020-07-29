FROM opensuse/tumbleweed:latest
LABEL mantainer william@blackhats.net.au

RUN zypper ar obs://home:firstyear:kanidm home_firstyear_kanidm && \
    zypper --gpg-auto-import-keys ref --force && \
    zypper install -y \
        kanidm-unixd-clients rsync system-user-nobody && \
    zypper clean -a

CMD ["rsync", "--daemon", "--log-file=/dev/stdout", "--no-detach"]


