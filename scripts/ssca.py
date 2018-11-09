# --- BEGIN COPYRIGHT BLOCK ---
# Copyright (C) 2015 Red Hat, Inc.
# Copyright (C) 2018 William Brown <william@blackhats.net.au>
# All rights reserved.
#
# License: GPL (version 3 or any later version).
# See LICENSE for details.
# --- END COPYRIGHT BLOCK ---

"""
Helper command based on 389ds lib389/nss_ssl.py, to make it easier
to manage certificate creation and signing.
"""

import argparse
import os
import sys
import random
import string
import re
import socket
import time
import shutil
import logging
import uuid
import subprocess
import shlex

from datetime import datetime, timedelta
from subprocess import check_output

# We don't have access to these in our command, so we have to import these
# in directly.
# from lib389.passwd import password_generate
# from lib389.utils import ensure_str, ensure_bytes, format_cmd_list


KEYBITS = 4096
CA_NAME = 'Self-Signed-CA'
CERT_NAME = 'Server-Cert'
USER_PREFIX = 'user-'
PIN_TXT = 'pin.txt'
PWD_TXT = 'pwdfile.txt'
CERT_SUFFIX = 'O=testing,L=389ds,ST=Queensland,C=AU'
ISSUER = 'CN=ssca.389ds.example.com,%s' % CERT_SUFFIX
SELF_ISSUER = 'CN={HOSTNAME},givenName={GIVENNAME},%s' % CERT_SUFFIX
USER_ISSUER = 'CN={HOSTNAME},%s' % CERT_SUFFIX
VALID = 24
VALID_MIN = 61  # Days

# My logger
log = None

### Directly copied from lib389

def password_generate(length=64):
    """Generate a complex password with at least
    one upper case letter, a lower case letter, a digit
    and a special character

    :param length: a password length
    :type length: int

    :returns: a string with a password
    """

    # We have exactly 64 characters because it makes the selection unbiased
    # The number of possible values for a byte is 256 which is a multiple of 64
    # Maybe it is an overkill for our case but it can come handy one day
    # (especially consider the fact we can use it for CLI tools)
    chars = string.ascii_letters + string.digits + '*&'

    # Get the minimal requirements
    pw = [random.choice(string.ascii_lowercase),
          random.choice(string.ascii_uppercase),
          random.choice(string.digits),
          '!']

    # Use the simple algorithm to generate more or less secure password
    for i in range(length - 3):
        # pw.append(chars[os.urandom(1)[0] % len(chars)])
        pw.append(random.choice(chars))
    random.shuffle(pw)
    return "".join(pw)


def format_cmd_list(cmd):
    """Format the subprocess command list to the quoted shell string"""

    # This only works on python 3
    if sys.version_info.major == 2:
        return " ".join(cmd)
    else:
        return " ".join(map(shlex.quote, cmd))


def ensure_bytes(val):
    if val != None and type(val) != bytes:
        return val.encode()
    return val


def ensure_str(val):
    if val != None and type(val) != str:
        try:
            result = val.decode('utf-8')
        except UnicodeDecodeError:
            # binary value, just return str repr?
            result = str(val)
        return result
    return val

### End direct lib389 copy


class NssSsl(object):
    def __init__(self, dirsrv=None, dbpassword=None, dbpath=None):
        self.dirsrv = dirsrv
        self._certdb = dbpath
        if self._certdb is None:
            self._certdb = self.dirsrv.get_cert_dir()
        self.log = log
        if self.dirsrv is not None:
            self.log = self.dirsrv.log
        if dbpassword is None:
            self.dbpassword = password_generate()
        else:
            self.dbpassword = dbpassword

        self.db_files = {"dbm_backend": ["%s/%s" % (self._certdb, f) for f in ("key3.db", "cert8.db", "secmod.db")],
                         "sql_backend": ["%s/%s" % (self._certdb, f) for f in ("key4.db", "cert9.db", "pkcs11.txt")],
                         "support": ["%s/%s" % (self._certdb, f) for f in ("noise.txt", "pin.txt", "pwdfile.txt")]}

    def detect_alt_names(self, alt_names=[]):
        """Attempt to determine appropriate subject alternate names for a host.
        Returns the list of names we derive.

        :param alt_names: A list of alternate names.
        :type alt_names: list[str]
        :returns: list[str]
        """
        if self.dirsrv and self.dirsrv.host not in alt_names:
            alt_names.append(self.dirsrv.host)
        if len(alt_names) == 0:
            alt_names.append(socket.gethostname())
        return alt_names

    def generate_cert_subject(self, alt_names=[]):
        """Return the cert subject we would generate for this host
        from the lib389 self signed process. This is *not* the subject
        of the actual cert, which could be different.

        :param alt_names: Alternative names you want to configure.
        :type alt_names: [str, ]
        :returns: String of the subject DN.
        """

        if self.dirsrv and len(alt_names) > 0:
            return SELF_ISSUER.format(GIVENNAME=self.dirsrv.get_uuid(), HOSTNAME=alt_names[0])
        elif len(alt_names) > 0:
            return SELF_ISSUER.format(GIVENNAME=uuid.uuid4(), HOSTNAME=alt_names[0])
        else:
            return SELF_ISSUER.format(GIVENNAME=uuid.uuid4(), HOSTNAME='lib389host.localdomain')

    def get_server_cert_subject(self, alt_names=[]):
        """Get the server db subject. For now, this uses generate, but later
        we can make this determined from other factors like x509 parsing.

        :returns: str
        """
        alt_names = self.detect_alt_names(alt_names)
        return self.generate_cert_subject(alt_names)

    def _generate_noise(self, fpath):
        noise = password_generate(256)
        with open(fpath, 'w') as f:
            f.write(noise)

    def reinit(self):
        """
        Re-init (create) the nss db.
        """
        # 48886: The DB that DS ships with is .... well, broken. Purge it!
        assert self.remove_db()

        try:
            os.makedirs(self._certdb)
        except FileExistsError:
            pass

        # In the future we may add the needed option to avoid writing the pin
        # files.
        # Write the pin.txt, and the pwdfile.txt
        if not os.path.exists('%s/%s' % (self._certdb, PIN_TXT)):
            with open('%s/%s' % (self._certdb, PIN_TXT), 'w') as f:
                f.write('Internal (Software) Token:%s' % self.dbpassword)
        if not os.path.exists('%s/%s' % (self._certdb, PWD_TXT)):
            with open('%s/%s' % (self._certdb, PWD_TXT), 'w') as f:
                f.write('%s' % self.dbpassword)

        # Init the db.
        # 48886; This needs to be sql format ...
        cmd = ['/usr/bin/certutil', '-N', '-d', self._certdb, '-f', '%s/%s' % (self._certdb, PWD_TXT)]
        self._generate_noise('%s/noise.txt' % self._certdb)
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        result = ensure_str(check_output(cmd, stderr=subprocess.STDOUT))
        self.log.debug("nss output: %s", result)
        return True

    def _db_exists(self):
        """Check that a nss db exists at the certpath"""

        if all(map(os.path.exists, self.db_files["dbm_backend"])) or \
           all(map(os.path.exists, self.db_files["sql_backend"])):
            return True
        return False

    def remove_db(self):
        """Remove nss db files at the certpath"""

        files = self.db_files["dbm_backend"] + \
                self.db_files["sql_backend"] + \
                self.db_files["support"]

        for file in files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

        if os.path.isdir(self._certdb) and not os.listdir(self._certdb):
            os.removedirs(self._certdb)

        assert not self._db_exists()
        return True

    def create_rsa_ca(self, months=VALID, subject=ISSUER):
        """
        Create a self signed CA.
        """

        # Wait a second to avoid an NSS bug with serial ids based on time.
        time.sleep(1)
        # Create noise.
        self._generate_noise('%s/noise.txt' % self._certdb)
        # Now run the command. Can we do this with NSS native?
        cmd = [
            '/usr/bin/certutil',
            '-S',
            '-n',
            CA_NAME,
            '-s',
            subject,
            '-x',
            '-g',
            '%s' % KEYBITS,
            '-t',
            'CT,,',
            '-v',
            '%s' % months,
            '--keyUsage',
            'certSigning',
            '-d',
            self._certdb,
            '-z',
            '%s/noise.txt' % self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        result = ensure_str(check_output(cmd, stderr=subprocess.STDOUT))
        self.log.debug("nss output: %s", result)
        # Now extract the CAcert to a well know place.
        # This allows us to point the cacert dir here and it "just works"
        cmd = [
            '/usr/bin/certutil',
            '-L',
            '-n',
            CA_NAME,
            '-d',
            self._certdb,
            '-a',
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        certdetails = check_output(cmd, stderr=subprocess.STDOUT)
        with open('%s/ca.crt' % self._certdb, 'w') as f:
            f.write(ensure_str(certdetails))
        cmd = ['/usr/bin/c_rehash', self._certdb]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)
        return True

    def rsa_ca_needs_renew(self):
        """Check is our self signed CA is expired or
        will expire less than a minimum period of time (VALID_MIN)
        """

        cmd = [
            '/usr/bin/certutil',
            '-L',
            '-n',
            CA_NAME,
            '-d',
            self._certdb,
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        certdetails = check_output(cmd, stderr=subprocess.STDOUT, encoding='utf-8')
        end_date_str = certdetails.split("Not After : ")[1].split("\n")[0]
        date_format = '%a %b %d %H:%M:%S %Y'
        end_date = datetime.strptime(end_date_str, date_format)

        if end_date - datetime.now() < timedelta(days=VALID_MIN):
            return True
        else:
            return False

    def renew_rsa_ca(self, months=VALID):
        """Renew the self signed CA."""

        csr_path = os.path.join(self._certdb, 'CA_renew.csr')
        crt_path = '%s/ca.crt' % self._certdb

        # Create noise.
        self._generate_noise('%s/noise.txt' % self._certdb)

        # Generate a CSR for a new CA cert
        cmd = [
            '/usr/bin/certutil',
            '-R',
            '-s',
            ISSUER,
            '-g',
            '%s' % KEYBITS,
            '-k',
            'NSS Certificate DB:%s' % CA_NAME,
            '-d',
            self._certdb,
            '-z',
            '%s/noise.txt' % self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
            '-a',
            '-o', csr_path,
            ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)

        # Sign the CSR with our old CA
        cmd = [
            '/usr/bin/certutil',
            '-C',
            '-d',
            self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
            '-a',
            '-i', csr_path,
            '-o', crt_path,
            '-c', CA_NAME,
            '--keyUsage',
            'certSigning',
            '-t',
            'CT,,',
            '-v',
            '%s' % months,
            ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)

        cmd = ['/usr/bin/c_rehash', self._certdb]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)

        # Import the new CA to our DB instead of the old CA
        cmd = [
            '/usr/bin/certutil',
            '-A',
            '-n', CA_NAME,
            '-t', "CT,,",
            '-a',
            '-i', crt_path,
            '-d', self._certdb,
            '-f', '%s/%s' % (self._certdb, PWD_TXT),
            ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)

        return crt_path

    def _rsa_cert_list(self):
        cmd = [
            '/usr/bin/certutil',
            '-L',
            '-d',
            self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
        ]
        result = ensure_str(check_output(cmd, stderr=subprocess.STDOUT))

        # We can skip the first few lines. They are junk
        # IE ['',
        #     'Certificate Nickname                                         Trust Attributes',
        #     '                                                             SSL,S/MIME,JAR/XPI',
        #     '',
        #     'Self-Signed-CA                                               CTu,u,u',
        #     '']
        lines = result.split('\n')[4:-1]
        # Now make the lines usable
        cert_values = []
        for line in lines:
            data = line.split()
            cert_values.append((data[0], data[1]))
        return cert_values

    def _rsa_cert_key_exists(self, cert_tuple):
        name = cert_tuple[0]
        cmd = [
            '/usr/bin/certutil',
            '-K',
            '-d',
            self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        result = ensure_str(check_output(cmd, stderr=subprocess.STDOUT))

        lines = result.split('\n')[1:-1]
        key_list = []
        for line in lines:
            m = re.match('\<(?P<id>.*)\> (?P<type>\w+)\s+(?P<hash>\w+).*:(?P<name>.+)', line)
            if name == m.group('name'):
                return True
        return False

    def _rsa_cert_is_catrust(self, cert_tuple):
        trust_flags = cert_tuple[1]
        (ssl_flag, mime_flag, jar_flag) = trust_flags.split(',')
        return 'C' in ssl_flag

    def _rsa_cert_is_user(self, cert_tuple):
        """
        Check an RSA cert is user trust

        Sadly we can't check for ext key usage, because NSS makes this really hard.
        """
        trust_flags = cert_tuple[1]
        (ssl_flag, mime_flag, jar_flag) = trust_flags.split(',')
        return 'u' in ssl_flag

    def _rsa_ca_exists(self):
        """
        Detect if a self-signed ca exists
        """
        have_ca = False
        cert_list = self._rsa_cert_list()
        for cert in cert_list:
            if self._rsa_cert_key_exists(cert) and self._rsa_cert_is_catrust(cert):
                have_ca = True
        return have_ca

    def _rsa_key_and_cert_exists(self):
        """
        Check if a valid server key and cert pair exist.
        """
        have_cert = False
        cert_list = self._rsa_cert_list()
        for cert in cert_list:
            # This could do a better check for !ca, and server attrs
            if self._rsa_cert_key_exists(cert) and not self._rsa_cert_is_catrust(cert):
                have_cert = True
        return have_cert

    def _rsa_user_exists(self, name):
        """
        Check if a valid server key and cert pair exist for a user.

        we use the format, user-<name>
        """
        have_user = False
        cert_list = self._rsa_cert_list()
        for cert in cert_list:
            if (cert[0] == '%s%s' % (USER_PREFIX, name)):
                if self._rsa_cert_key_exists(cert) and self._rsa_cert_is_user(cert):
                    have_user = True
        return have_user

    def create_rsa_key_and_cert(self, alt_names=[], months=VALID):
        """
        Create a key and a cert that is signed by the self signed ca

        This will use the hostname from the DS instance, and takes a list of
        extra names to take.
        """

        alt_names = self.detect_alt_names(alt_names)
        subject = self.generate_cert_subject(alt_names)

        # Wait a second to avoid an NSS bug with serial ids based on time.
        time.sleep(1)
        # Create noise.
        self._generate_noise('%s/noise.txt' % self._certdb)
        cmd = [
            '/usr/bin/certutil',
            '-S',
            '-n',
            CERT_NAME,
            '-s',
            subject,
            # We MUST issue with SANs else ldap wont verify the name.
            '-8', ','.join(alt_names),
            '-c',
            CA_NAME,
            '-g',
            '%s' % KEYBITS,
            '-t',
            ',,',
            '-v',
            '%s' % months,
            '-d',
            self._certdb,
            '-z',
            '%s/noise.txt' % self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        result = ensure_str(check_output(cmd, stderr=subprocess.STDOUT))
        self.log.debug("nss output: %s", result)
        return True

    def create_rsa_key_and_csr(self, alt_names=[], subject=None):
        """Create a new RSA key and the certificate signing request. This
        request can be submitted to a CA for signing. The returned certifcate
        can be added with import_rsa_crt.
        """
        csr_path = os.path.join(self._certdb, '%s.csr' % CERT_NAME)

        alt_names = self.detect_alt_names(alt_names)
        if subject is None:
            subject = self.generate_cert_subject(alt_names)

        # Wait a second to avoid an NSS bug with serial ids based on time.
        time.sleep(1)
        # Create noise.
        self._generate_noise('%s/noise.txt' % self._certdb)

        cmd = [
            '/usr/bin/certutil',
            '-R',
            # We want a dual purposes client and server cert
            '--keyUsage',
            'digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment',
            '--nsCertType',
            'sslClient,sslServer',
            '--extKeyUsage',
            'clientAuth,serverAuth',
            '-s',
            subject,
            # We MUST issue with SANs else ldap wont verify the name.
            '-8', ','.join(alt_names),
            '-g',
            '%s' % KEYBITS,
            '-d',
            self._certdb,
            '-z',
            '%s/noise.txt' % self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
            '-a',
            '-o', csr_path,
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)

        return csr_path

    def rsa_ca_sign_csr(self, csr_path, months=VALID):
        """ Given a CSR, sign it with our CA certificate (if present). This
        emits a signed certificate which can be imported with import_rsa_crt.
        """
        crt_path = 'crt'.join(csr_path.rsplit('csr', 1))
        ca_path = '%s/ca.crt' % self._certdb

        cmd = [
            '/usr/bin/certutil',
            '-C',
            '-d',
            self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
            '-v',
            '%s' % months,
            '-a',
            '-i', csr_path,
            '-o', crt_path,
            '-c', CA_NAME,
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)

        return (ca_path, crt_path)

    def import_rsa_crt(self, ca=None, crt=None):
        """Given a signed certificate from a ca, import the CA and certificate
        to our database.


        """

        assert ca is not None or crt is not None, "At least one parameter should be specified (ca or crt)"

        if ca is not None:
            shutil.copyfile(ca, '%s/ca.crt' % self._certdb)
            cmd = [
                '/usr/bin/certutil',
                '-A',
                '-n', CA_NAME,
                '-t', "CT,,",
                '-a',
                '-i', '%s/ca.crt' % self._certdb,
                '-d', self._certdb,
                '-f',
                '%s/%s' % (self._certdb, PWD_TXT),
            ]
            self.log.debug("nss cmd: %s", format_cmd_list(cmd))
            check_output(cmd, stderr=subprocess.STDOUT)

        if crt is not None:
            cmd = [
                '/usr/bin/certutil',
                '-A',
                '-n', CERT_NAME,
                '-t', ",,",
                '-a',
                '-i', crt,
                '-d', self._certdb,
                '-f',
                '%s/%s' % (self._certdb, PWD_TXT),
            ]
            self.log.debug("nss cmd: %s", format_cmd_list(cmd))
            check_output(cmd, stderr=subprocess.STDOUT)
            cmd = [
                '/usr/bin/certutil',
                '-V',
                '-d', self._certdb,
                '-n', CERT_NAME,
                '-u', 'YCV'
            ]
            self.log.debug("nss cmd: %s", format_cmd_list(cmd))
            check_output(cmd, stderr=subprocess.STDOUT)

            # Now extract the private key and p12 to usable types.

            cmd = [
                'pk12util',
                '-d', self._certdb,
                '-o', '%s/%s.p12' % (self._certdb, CERT_NAME),
                '-k', '%s/%s' % (self._certdb, PWD_TXT),
                '-n', CERT_NAME,
                '-W', '""'
            ]
            self.log.debug("nss cmd: %s", format_cmd_list(cmd))
            check_output(cmd, stderr=subprocess.STDOUT)
            # openssl pkcs12 -in user-william.p12 -passin pass:'' -out file.pem -nocerts -nodes
            # Extract the key
            cmd = [
                'openssl',
                'pkcs12',
                '-in', '%s/%s.p12' % (self._certdb, CERT_NAME),
                '-passin', 'pass:""',
                '-out', '%s/server.pem.key' % self._certdb,
                '-nocerts',
                '-nodes'
            ]
            self.log.debug("nss cmd: %s", format_cmd_list(cmd))
            check_output(cmd, stderr=subprocess.STDOUT)
            # Extract the cert
            cmd = [
                'openssl',
                'pkcs12',
                '-in', '%s/%s.p12' % (self._certdb, CERT_NAME),
                '-passin', 'pass:""',
                '-out', '%s/server.pem.crt' % self._certdb,
                '-nokeys',
                '-clcerts',
                '-nodes'
            ]
            self.log.debug("nss cmd: %s", format_cmd_list(cmd))
            check_output(cmd, stderr=subprocess.STDOUT)
            # Convert the cert for userCertificate attr
            cmd = [
                'openssl',
                'x509',
                '-inform', 'PEM',
                '-outform', 'DER',
                '-in', '%s/server.pem.crt' % self._certdb,
                '-out', '%s/server.der.crt' % self._certdb,
            ]
            self.log.debug("nss cmd: %s", format_cmd_list(cmd))
            check_output(cmd, stderr=subprocess.STDOUT)

        # Rehash all the contents
        cmd = ['/usr/bin/c_rehash', self._certdb]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)

    def create_rsa_user(self, name, months=VALID):
        """
        Create a key and cert for a user to authenticate to the directory.

        Name is the uid of the account, and will become the CN of the cert.
        """
        subject = USER_ISSUER.format(HOSTNAME=name)
        if self._rsa_user_exists(name):
            return subject

        # Wait a second to avoid an NSS bug with serial ids based on time.
        time.sleep(1)
        cmd = [
            '/usr/bin/certutil',
            '-S',
            '-n',
            '%s%s' % (USER_PREFIX, name),
            '-s',
            subject,
            '--keyUsage',
            'digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment',
            '--nsCertType',
            'sslClient',
            '--extKeyUsage',
            'clientAuth',
            '-c',
            CA_NAME,
            '-g',
            '%s' % KEYBITS,
            '-t',
            ',,',
            '-v',
            '%s' % months,
            '-d',
            self._certdb,
            '-z',
            '%s/noise.txt' % self._certdb,
            '-f',
            '%s/%s' % (self._certdb, PWD_TXT),
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))

        result = ensure_str(check_output(cmd, stderr=subprocess.STDOUT))
        self.log.debug("nss output: %s", result)
        # Now extract this into PEM files that we can use.
        # pk12util -o user-william.p12 -d . -k pwdfile.txt -n user-william -W ''
        cmd = [
            'pk12util',
            '-d', self._certdb,
            '-o', '%s/%s%s.p12' % (self._certdb, USER_PREFIX, name),
            '-k', '%s/%s' % (self._certdb, PWD_TXT),
            '-n', '%s%s' % (USER_PREFIX, name),
            '-W', '""'
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)
        # openssl pkcs12 -in user-william.p12 -passin pass:'' -out file.pem -nocerts -nodes
        # Extract the key
        cmd = [
            'openssl',
            'pkcs12',
            '-in', '%s/%s%s.p12' % (self._certdb, USER_PREFIX, name),
            '-passin', 'pass:""',
            '-out', '%s/%s%s.key' % (self._certdb, USER_PREFIX, name),
            '-nocerts',
            '-nodes'
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)
        # Extract the cert
        cmd = [
            'openssl',
            'pkcs12',
            '-in', '%s/%s%s.p12' % (self._certdb, USER_PREFIX, name),
            '-passin', 'pass:""',
            '-out', '%s/%s%s.crt' % (self._certdb, USER_PREFIX, name),
            '-nokeys',
            '-clcerts',
            '-nodes'
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)
        # Convert the cert for userCertificate attr
        cmd = [
            'openssl',
            'x509',
            '-inform', 'PEM',
            '-outform', 'DER',
            '-in', '%s/%s%s.crt' % (self._certdb, USER_PREFIX, name),
            '-out', '%s/%s%s.der' % (self._certdb, USER_PREFIX, name),
        ]
        self.log.debug("nss cmd: %s", format_cmd_list(cmd))
        check_output(cmd, stderr=subprocess.STDOUT)

        return subject

    def get_rsa_user(self, name):
        """
        Return a dict of information for ca, key and cert paths for the user id
        """
        ca_path = '%s/ca.crt' % self._certdb
        key_path = '%s/%s%s.key' % (self._certdb, USER_PREFIX, name)
        crt_path = '%s/%s%s.crt' % (self._certdb, USER_PREFIX, name)
        crt_der_path = '%s/%s%s.der' % (self._certdb, USER_PREFIX, name)
        return {'ca': ca_path, 'key': key_path, 'crt': crt_path, 'crt_der_path': crt_der_path}

def ssca_create(args):
    # Need args path
    # need issuer cn/string
    # Write the issuer?
    ssca = NssSsl(dbpath=args.dbpath)
    ssca.reinit()
    ssca.create_rsa_ca(subject=args.subject)

def ssca_renew(args):
    ssca = NssSsl(dbpath=args.dbpath)
    # Needs time?
    if ssca.rsa_ca_needs_renew():
        # Read issuer from file into the renew.
        ssca.renew_rsa_ca()

def ssca_sign(args):
    ssca = NssSsl(dbpath=args.dbpath)
    # Needs paths
    # needs valid time
    (ca_path, crt_path) = ssca.rsa_ca_sign_csr(args.csr_path)
    log.info('ca: %s' % ca_path)
    log.info('crt: %s' % crt_path)

def client_init(args):
    ssca = NssSsl(dbpath=args.dbpath)
    ssca.reinit()

def user_request(args):
    # Probably need a few details
    ssdb = NssSsl(dbpath=args.dbpath)

def server_request(args):
    # Alt names
    # subject
    ssdb = NssSsl(dbpath=args.dbpath)
    alt_names = args.alt_names.split(',')
    csr_path = ssdb.create_rsa_key_and_csr(alt_names=alt_names, subject=args.subject)
    log.info('csr: %s' % csr_path)

def user_accept(args):
    # Needs path of db and path to crt + ca
    # Needs cert nickname?
    ssdb = NssSsl(dbpath=args.dbpath)
    ssdb.import_rsa_crt(args.ca, args.crt)

def server_accept(args):
    # Needs path of db and path to crt + ca
    # Needs name of the CA nickname?
    ssdb = NssSsl(dbpath=args.dbpath)
    ssdb.import_rsa_crt(args.ca_path, args.crt_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage and request certs with a simple self-signed CA.')

    ## Common options
    parser.add_argument('-v', '--verbose', help="Verbose", action='store_true', default=False)

    ## Subparsers for all the main commands
    subparsers = parser.add_subparsers(help="Actions to perform.")

    ssca_create_parser = subparsers.add_parser('ssca_create', help="Create a new self signed CA")
    ssca_create_parser.set_defaults(func=ssca_create)
    ssca_create_parser.add_argument('-d', '--dbpath', help="Path to the SSCA folder", required=True)
    ssca_create_parser.add_argument('-s', '--subject', help="The CA subject line in form of: CN=<>,O=<>,L=<>,ST=<>,C=<>", required=True)
    # ssca_create_parser.add_argument('-s', '--subject', help="", required=True)

    ssca_renew_parser = subparsers.add_parser('ssca_renew', help="Renew the self signed CA")
    ssca_renew_parser.set_defaults(func=ssca_renew)

    ssca_sign_parser = subparsers.add_parser('ssca_sign', help="Sign a request with the self signed CA")
    ssca_sign_parser.set_defaults(func=ssca_sign)
    ssca_sign_parser.add_argument('-d', '--dbpath', help="Path to the SSCA folder", required=True)
    ssca_sign_parser.add_argument('-r', '--csr_path', help="Path to the x509 csr", required=True)

    client_init_parser = subparsers.add_parser('client_init', help="Create a new client db")
    client_init_parser.set_defaults(func=client_init)
    client_init_parser.add_argument('-d', '--dbpath', help="Path to the user db folder", required=True)

    user_request_parser = subparsers.add_parser('user_request', help="Create a user certificate signing request")
    user_request_parser.set_defaults(func=user_request)
    user_request_parser.add_argument('-d', '--dbpath', help="Path to the user db folder", required=True)

    server_request_parser = subparsers.add_parser('server_request', help="Create a server certificate signing request")
    server_request_parser.set_defaults(func=server_request)
    server_request_parser.add_argument('-d', '--dbpath', help="Path to the user db folder", required=True)
    server_request_parser.add_argument('-s', '--subject', help="The subject line in form of: CN=<>,O=<>,L=<>,ST=<>,C=<>", required=True)
    server_request_parser.add_argument('-a', '--alt_names', help="Subject alt names as a comma seperated list", required=True)

    user_accept_parser = subparsers.add_parser('user_accept', help="Accept a user certificate signed by the CA")
    user_accept_parser.set_defaults(func=user_accept)
    user_accept_parser.add_argument('-d', '--dbpath', help="Path to the user db folder", required=True)

    server_accept_parser = subparsers.add_parser('server_accept', help="Create a server certificate signed by the CA")
    server_accept_parser.set_defaults(func=server_accept)
    server_accept_parser.add_argument('-d', '--dbpath', help="Path to the user db folder", required=True)
    server_accept_parser.add_argument('-c', '--ca_path', help="Path to the signing CA cert", required=True)
    server_accept_parser.add_argument('-i', '--crt_path', help="Path to the signed cert", required=True)


    args = parser.parse_args()
    # Get the verbose flag if needed
    root = logging.getLogger()
    log = logging.getLogger('ssca')
    log_handler = logging.StreamHandler()

    if args.verbose:
        log.setLevel(logging.DEBUG)
        log_format = '%(levelname)s: %(message)s'
    else:
        log.setLevel(logging.INFO)
        log_format = '%(message)s'

    log_handler.setFormatter(logging.Formatter(log_format))
    root.addHandler(log_handler)

    # Call the related function
    if hasattr(args, 'func') is False:
        parser.print_help()
        sys.exit(1)

    args.func(args)



