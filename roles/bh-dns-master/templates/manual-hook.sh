#!/bin/bash

# First, remove any old records.
# Now write the new challenge
cat > /tmp/nsupdate-cmd.txt << EOF
server ::1 
ttl 60
update delete _acme-challenge.${CERTBOT_DOMAIN}. TXT
update add _acme-challenge.${CERTBOT_DOMAIN}. 60 TXT "${CERTBOT_VALIDATION}"
send
EOF

nsupdate -k /etc/named.ns1.blackhats.net.au.key /tmp/nsupdate-cmd.txt

# Let the TTL expire.

sleep 70

