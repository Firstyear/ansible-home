FROM opensuse/tumbleweed:latest
LABEL mantainer william@blackhats.net.au

RUN zypper ar obs://home:firstyear:kanidm home_firstyear_kanidm && \
    zypper --gpg-auto-import-keys ref --force && \
    zypper install -y \
        kanidm-unixd-clients samba && \
    zypper clean -a

CMD ["smbd", "-FS", "--no-process-group"]

