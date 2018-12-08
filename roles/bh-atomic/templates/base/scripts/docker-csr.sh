#!/bin/sh

certutil -N -d .
echo certutil -d . -R -a -o client.csr -g 4096 -Z SHA256 -v 24 -s "CN=$(cat /etc/hostname),O=Blackhats,L=Brisbane,ST=Queensland,C=AU"
certutil -d . -R -a -o client.csr -g 4096 -Z SHA256 -v 24 -s "CN=$(cat /etc/hostname),O=Blackhats,L=Brisbane,ST=Queensland,C=AU"

vim client.csr
vim client.cert

certutil -d . -A -n 'docker' -t ",," -i client.cert
pk12util -o server-export.p12 -d . -n 'docker'
openssl pkcs12 -in server-export.p12 -out client.key -nocerts -nodes


