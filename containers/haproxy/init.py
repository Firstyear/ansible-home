#!/usr/bin/python3

import os
import sys
import subprocess

def do_main():
    print(os.environ)

    target_host = os.environ.get('HAPROXY_TARGET', 'www')
    target_port = os.environ.get('HAPROXY_TARGET_PORT', '80')
    hostname = os.environ.get('HAPROXY_HOSTNAME', 'localhost')
    linode_key = os.environ.get('HAPROXY_LINODE_KEY', None)

    raw_target_port = os.environ.get('HAPROXY_RAW_TARGET_PORT', None)
    raw_listen_port = os.environ.get('HAPROXY_RAW_LISTEN_PORT', None)

    extra = ''


    if linode_key is not None:
        # Given the linode_key, attempt a certbot setup/renew
        with open("/tmp/linode.ini", 'w') as f:
            f.write(f"""
dns_linode_key = {linode_key}
dns_linode_version =
""")
        subprocess.call([
            "certbot",
            "certonly",
            "--dns-linode",
            "--dns-linode-credentials", "/tmp/linode.ini",
            "--dns-linode-propagation-seconds", "1000",
            "-d", hostname,
            "-m", "william@blackhats.net.au",
            "--agree-tos", "-n"
        ])
        # Done, now lets stich them together.

    cpath = None

    if os.path.exists(f'/etc/letsencrypt/live/{hostname}/privkey.pem'):
        cpath = 'letsencrypt'
    elif os.path.exists(f'/etc/certbot/live/{hostname}/privkey.pem'):
        cpath = 'certbot'
    else:
        print("Could not find valid privkey!")

        try:
            print("== letsencrypt")
            print(os.listdir('/etc/letsencrypt/live'))
        except:
            pass

        try:
            print("== certbot")
            print(os.listdir('/etc/certbot/live'))
        except:
            pass

        sys.exit(1)

    print(f"Using certpath -> {cpath}")

    # Concat the two certs properly
    with open(f'/etc/{cpath}/live/{hostname}/bundle.pem', 'w') as k:
        with open(f'/etc/{cpath}/live/{hostname}/fullchain.pem', 'r') as f:
            k.write(f.read())
        with open(f'/etc/{cpath}/live/{hostname}/privkey.pem', 'r') as f:
            k.write(f.read())

    if raw_target_port and raw_listen_port:
        extra = f"""
frontend service_front
  bind 0.0.0.0:{raw_listen_port} ssl crt /etc/CERTPATH/live/HOSTNAME/bundle.pem
  mode tcp
  default_backend service

backend service
  mode tcp
  server s1 TARGET_HOST:{raw_target_port}
"""

    lines = None
    with open('/etc/haproxy/haproxy-template.cfg', 'r') as f:
        lines = f.readlines()

    with open('/etc/haproxy/haproxy.cfg', 'w') as f:
        for l in lines:
            l1 = l.replace('EXTRA', extra)
            l2 = l1.replace('TARGET_HOST', target_host)
            l3 = l2.replace('TARGET_PORT', target_port)
            l4 = l3.replace('HOSTNAME', hostname)
            l5 = l4.replace('CERTPATH', cpath)
            f.write(l5)

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



