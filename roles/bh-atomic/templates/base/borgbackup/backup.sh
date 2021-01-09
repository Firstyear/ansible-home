#!/bin/sh
export BORG_REPO={{ borgbasename }}@{{ borgbasename }}.repo.borgbase.com:repo
export BORG_PASSPHRASE={{ borgbasepw }}

borg create                         \
    --verbose                       \
    --filter AME                    \
    --list                          \
    --stats                         \
    --show-rc                       \
    --exclude-caches                \
    --exclude '*/.zfs'               \
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
    /mnt/comp/home/charcol/important \
    /mnt/comp/kanidm                \
    /mnt/comp/nextcloud             \
    /mnt/nextcloud_db               \
    /mnt/unifi_data                 \
    /root

borg prune                          \
    --list                          \
    --prefix '{hostname}-'          \
    --show-rc                       \
    --keep-within 7d

