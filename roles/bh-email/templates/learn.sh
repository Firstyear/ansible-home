#!/bin/zsh
cd /var/lib/dovecot/vmail/william
for i in {\
.INBOX.adelaide,\
.INBOX.389-users,\
.INBOX.self,\
.INBOX.freeipa,\
.INBOX.freeipa-devel,\
.INBOX.389-devel,\
.INBOX.fedora-devel,\
.INBOX.bugzilla,\
.archive,\
.archive.2013,\
.archive.2014,\
.archive.2015,\
.archive.2015.389-users,\
.archive.2015.bugzilla,\
.archive.2015.389-devel,\
.archive.2015.self,\
.archive.2015.fedora-devel,\
.archive.2015.adelaide,\
.archive.2015.freeipa-devel,\
.archive.2015.freeipa,\
.archive.2015.centos,\
.archive.2015.freebsd,\
.archive.2015.sssd-devel,\
.archive.2015.erlang,\
.\
};
do
    echo $i
    sa-learn --progress --no-sync --ham $i/{cur,new}
done
sa-learn --progress --no-sync --spam .INBOX.spam/{cur,new}
sa-learn --progress --no-sync --spam .archive.2015.spam/{cur,new}
sa-learn --progress --sync

