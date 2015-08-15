#!/bin/zsh
cd /var/lib/dovecot/vmail/william
sa-learn --progress --no-sync --ham {.INBOX.389-devel,.INBOX.389-users,.archive,.archive.2013,.archive.2014,.archive.2015,.archive.2015.fedora,.archive.2015.fedora-devel,.archive.2015.freeipa,.archive.2015.sssd-devel,.INBOX.bugzilla,.archive.2015.centos,.archive.2015.erlang,.INBOX.fedora-devel,.archive.2015.freebsd,.INBOX.freeipa,.INBOX.freeipa-devel,.INBOX.self,.}/{cur,new}
sa-learn --progress --no-sync --spam .INBOX.spam/{cur,new}
sa-learn --progress --sync

