FROM registry:2

# This is the information to allow ATOMIC to install and run this.
LABEL "Name"="atomic-registry"
LABEL INSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -v /var/lib/\${NAME}:/var/lib/registry -e NAME=${NAME} -e IMAGE=${IMAGE} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/install.sh \${OPT3}"
LABEL UNINSTALL "/usr/bin/docker run -t -i --rm \${OPT1} --privileged -v /:/host -v /var/lib/\${NAME}:/var/lib/registry -e NAME=${NAME} --name \${NAME} \${IMAGE} \${OPT2} /bin/sh /bin/uninstall.sh \${OPT3}"
LABEL RUN '/usr/bin/docker run -t -i --rm \${OPT1} -v /var/lib/\${NAME}:/var/lib/registry -p 3128:3128 --name \${NAME} \${IMAGE} \${OPT2}'

COPY install.sh /bin/
COPY uninstall.sh /bin/

