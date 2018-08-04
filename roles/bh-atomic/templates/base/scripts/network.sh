#!/bin/bash

DEV=$(ip route | grep ^default | sed 's/^.* dev //;s/ .*$//'|head -1)
if [ -n "$DEV" ]
then
     IP_AND_PREFIX_LEN=$(ip -f inet addr show dev $DEV | grep 'inet '| head -1 | sed 's/^ *inet *//;s/ .*$//')
     IP=$(echo ${IP_AND_PREFIX_LEN} | cut -f1 -d'/')
     MASK=$(ipcalc -m ${IP_AND_PREFIX_LEN} | sed 's/^.*=//')
     GW=$(ip route | grep default | head -1 | sed 's/^.*via //;s/ .*$//')
     IP6_PREFIX=$(ip -f inet6 addr show dev $DEV | grep 'inet6 '| head -1 | sed 's/^ *inet6 *//;s/ .*$//')
     IP6=$(echo ${IP6_PREFIX} | cut -f1 -d'/')
     MASK6=$(echo ${IP6_PREFIX} | cut -f2 -d'/')
     # GW6=$(ip -6 route | grep default | head -1 | sed 's/^.*via //;s/ .*$//')
     GW6=$(echo `echo ${IP6_PREFIX} | cut -f1,2,3,4 -d':'`::1 )
     MAC=$(ip link show dev ${DEV} | grep 'link/ether '| head -1 | sed 's/^ *link\/ether *//;s/ .*$//')

cat > /etc/sysconfig/network-scripts/ifcfg-${DEV} << DEVEOF
# Generated by magic
DEVICE=${DEV}
ONBOOT=yes
NETBOOT=no
BOOTPROTO=static
TYPE=Ethernet
NAME=${DEV}
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6_FAILURE_FATAL=yes
IPV6INIT=yes
PEERDNS=no
PEERROUTES=no
IPV6_AUTOCONF=no
# HWADDR=${MAC}
IPADDR=${IP}
GATEWAY=${GW}
NETMASK=${MASK}
IPV6ADDR=${IP6}
#PREFIX=${MASK6}
IPV6_DEFAULTGW=${GW6}
DNS1=2001:44b8:2155:2c16::15
DNS2=172.24.16.15
#NM_CONTROLLED=no

DEVEOF

    #Done
fi
