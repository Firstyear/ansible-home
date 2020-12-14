#!/usr/bin/python3

import os
import sys
import subprocess
import time

def do_main():
    print(os.environ)
    hostname = os.environ.get('LE_HOSTNAME', 'localhost')
    linode_key = os.environ.get('LE_LINODE_KEY', None)

    if linode_key is None:
        print("FAILED TO RUN CERTBOT, MUST SET LE_LINODE_KEY")

    while True:
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

        print("nap time ... zzzz ...")
        time.sleep(86400)


if __name__ == '__main__':
    do_main()



