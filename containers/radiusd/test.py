
import radiusd
import hashlib
import binascii

GUEST_PASS = hashlib.new('md4', "reallylongenablepassword".encode('utf-16le')).digest()
ADMIN_PASS = hashlib.new('md4', "reallylongadminpassword".encode('utf-16le')).digest()


USERS = {
    'guest': (GUEST_PASS, '13'),
    'admin': (ADMIN_PASS, '12'),
}


def instantiate(args):
    print(args)
    return radiusd.RLM_MODULE_OK


def authorize(args):
    radiusd.radlog(radiusd.L_INFO, 'python module called')

    dargs = dict(args)
    print(dargs)

    username = dargs['User-Name']

    userrec = USERS.get(username, None)
    if userrec is None:
        return radiusd.RLM_MODULE_NOTFOUND

    (usernthash, uservlan) = userrec

    reply = (
        ('Reply-Message', 'Welcome'),
        ('Group', 'Group-A'),
        ('Tunnel-Type', '13'),
        ('Tunnel-Medium-Type', '6'),
        ('Tunnel-Private-Group-ID', uservlan),
    )
    config = (
        ('NT-Password', usernthash),
    )

    return (radiusd.RLM_MODULE_OK, reply, config)

