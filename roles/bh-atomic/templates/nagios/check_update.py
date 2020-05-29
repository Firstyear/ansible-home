import subprocess;
import os
import sys
rc = subprocess.call(['systemctl', 'status', 'transactional-update.service'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL);
if rc == 3 or rc == 0:
    print("TRANSUPDATE OK: %d" % rc);
    # sys.stderr.write("TRANSUPDATE OK: %d\n" % rc);
else:
    print("TRANSUPDATE WARNING: %d" % rc);
    # sys.stderr.write("TRANSUPDATE WARNING: %d\n" % rc);
    sys.exit(1)


