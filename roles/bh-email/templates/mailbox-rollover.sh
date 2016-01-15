#!/bin/bash

# usage: doveadm [-Dv] [-f <formatter>] mailbox <command> [<args>]
#  create       [-u <user>|-A] [-S <socket_path>] [-s] [-g <guid>] <mailbox> [...]
#  delete       [-u <user>|-A] [-S <socket_path>] [-s] <mailbox> [...]
#  list         [-u <user>|-A] [-S <socket_path>] [-7|-8] [-s] [<mailbox mask> [...]]
#  mutf7        [-7|-8] <name> [...]
#  rename       [-u <user>|-A] [-S <socket_path>] [-s] <old name> <new name>
#  status       [-u <user>|-A] [-S <socket_path>] [-t] <fields> <mailbox mask> [...]
#  subscribe    [-u <user>|-A] [-S <socket_path>] <mailbox> [...]
#  unsubscribe  [-u <user>|-A] [-S <socket_path>] <mailbox> [...]

export MAILUSER='william@blackhats.net.au'
export LASTYEAR='2015'
export THISYEAR='2016'

# Stop postfix first
systemctl stop postfix

# Now we can fiddle with mailboxes
echo ${MAILUSER}
echo ${LASTYEAR}
echo ${THISYEAR}

# First, we want to make the new archive.

doveadm mailbox create -u ${MAILUSER} archive.${THISYEAR}

# Create a list of mailboxes.

export MAILBOXES=`doveadm mailbox list -u ${MAILUSER} 'INBOX.*' | awk -F '.' '{print $2}'`
echo $MAILBOXES

# Now move the directories to archive.
# Create the new equivalents

for MAILBOX in ${MAILBOXES}
do
    doveadm mailbox rename -u ${MAILUSER} INBOX.${MAILBOX} archive.${LASTYEAR}.${MAILBOX}
    doveadm mailbox subscribe -u ${MAILUSER} archive.${LASTYEAR}.${MAILBOX}
    doveadm mailbox create -u ${MAILUSER} INBOX.${MAILBOX}
done

doveadm mailbox list -u ${MAILUSER}

# Start postfix back up

systemctl start postfix



