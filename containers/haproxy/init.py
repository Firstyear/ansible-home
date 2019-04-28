#!/usr/bin/python3

import os
import subprocess

def do_main():
    print(os.environ)

    target_host = os.environ.get('HAPROXY_TARGET', 'www')
    hostname = os.environ.get('HAPROXY_HOSTNAME', 'localhost')

    # Concat the two certs properly
    with open('/etc/certbot/live/%s/bundle.pem' % hostname, 'w') as k:
        with open('/etc/certbot/live/%s/fullchain.pem' % hostname, 'r') as f:
            k.write(f.read())
        with open('/etc/certbot/live/%s/privkey.pem' % hostname, 'r') as f:
            k.write(f.read())

    lines = None
    with open('/etc/haproxy/haproxy-template.cfg', 'r') as f:
        lines = f.readlines()

    with open('/etc/haproxy/haproxy.cfg', 'w') as f:
        for l in lines:
            l1 = l.replace('TARGET_HOST', target_host)
            l2 = l1.replace('HOSTNAME', hostname)
            f.write(l2)

    subprocess.call([
        'cat',
        '/etc/haproxy/haproxy.cfg',
    ])
    # Template the config
    subprocess.call([
        '/usr/sbin/haproxy',
        '-f',
        '/etc/haproxy/haproxy.cfg',
        '-db',
    ])


if __name__ == '__main__':
    do_main()



