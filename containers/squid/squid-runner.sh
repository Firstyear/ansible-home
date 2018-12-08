#!/bin/sh

# Fix all our log dirs
mkdir -p /var/log/squid
chown -R squid:squid /var/log/squid
chmod 755 /var/log/squid

# Make sure we can access the spool
chown -R squid:squid /var/spool/squid
chmod 755 /var/spool/squid
# Make sure the swap dirs exist
/usr/sbin/squid -z --foreground
# Now run
/usr/sbin/squid --foreground

