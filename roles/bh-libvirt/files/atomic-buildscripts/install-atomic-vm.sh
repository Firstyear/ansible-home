#!/bin/bash
if [ -z ${1} ]
then
    echo "Must provide a VM name."
    exit 1
fi

DISKSIZE=20
MIRROR=ostree.net.blackhats.net.au
KSNAME=${1}.cfg
KSPATH=/root/vmscripts/ks/${KSNAME}
NETIF=net_servers
CENTOS_VERSION=7

virt-install --connect=qemu:///system -n $1 \
    --os-variant=rhel7 \
    --ram=2048 --vcpus=1 --security type=dynamic \
    --serial pty \
    --disk path=/var/lib/exports/t1/def_t1_nfs_sas/${1}.img,sparse=true,format=raw,bus=virtio,size=${DISKSIZE} \
    --location=http://${MIRROR}/pub/centos/7/os/x86_64/ \
    --network=bridge=${NETIF} \
    --extra-args "ks=http://${MIRROR}/ks/${KSNAME} console=ttyS0 cmdline ip=dhcp"
    #--initrd-inject=${KSPATH} \
    #--extra-args "ks=file:/${KSNAME} console=ttyS0 cmdline ip=auto6"
    #--graphics spice --extra-args "ks=file:///${KSNAME} " 

