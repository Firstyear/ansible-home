#!/bin/sh

export BORG_REPO=ssh://backup@topaz.prd.blackhats.net.au:22/home/backup/$(cat /etc/hostname)

borg create                         \
    --verbose                       \
    --filter AME                    \
    --list                          \
    --stats                         \
    --show-rc                       \
    --exclude-caches                \
    --exclude '/home/*/.cache/*'    \
    --exclude '/var/cache/*'        \
    --exclude '/var/tmp/*'          \
    --exclude '/.snapshots'         \
    --exclude '/bin' \
    --exclude '/usr' \
    --exclude '/boot' \
    --exclude '/dev' \
    --exclude '/data' \
    --exclude '/proc' \
    --exclude '/sbin' \
    ::'{hostname}-{now}'            \
    /etc                            \
    /home                           \
    /root                           \
    /var/lib/docker/volumes/

borg prune                          \
    --list                          \
    --prefix '{hostname}-'          \
    --show-rc                       \
    --keep-within 7d

export BORG_REPO={{ borgbasename }}@{{ borgbasename }}.repo.borgbase.com:repo
export BORG_PASSPHRASE={{ borgbasepw }}

borg create                         \
    --verbose                       \
    --filter AME                    \
    --list                          \
    --stats                         \
    --show-rc                       \
    --exclude-caches                \
    --exclude '/home/*/.cache/*'    \
    --exclude '/var/cache/*'        \
    --exclude '/var/tmp/*'          \
    --exclude '/.snapshots'         \
    --exclude '/bin' \
    --exclude '/usr' \
    --exclude '/boot' \
    --exclude '/dev' \
    --exclude '/data' \
    --exclude '/proc' \
    --exclude '/sbin' \
    ::'{hostname}-{now}'            \
    /etc                            \
    /home                           \
    /root                           \
    /var/lib/docker/volumes/

borg prune                          \
    --list                          \
    --prefix '{hostname}-'          \
    --show-rc                       \
    --keep-within 14d

