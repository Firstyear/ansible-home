#!/bin/bash

DEV=$(ip route | grep ^default | sed 's/^.* dev //;s/ .*$//'|head -1)
if [ -n "$DEV" ]
then
     IP_AND_PREFIX_LEN=$(ip -f inet addr show dev $DEV | grep 'inet '| head -1 | sed 's/^ *inet *//;s/ .*$//')
     GW=$(ip route | grep default | head -1 | sed 's/^.*via //;s/ .*$//')
     IP6_PREFIX=$(ip -f inet6 addr show dev $DEV | grep 'inet6 ' | grep -v temporary | grep global | head -1 | sed 's/^ *inet6 *//;s/ .*$//')
     # GW6=$(ip -6 route | grep default | head -1 | sed 's/^.*via //;s/ .*$//')
     GW6=$(echo `echo ${IP6_PREFIX} | cut -f1,2,3,4 -d':'`::1 )

cat > /etc/sysconfig/network/ifcfg-${DEV} << DEVEOF
# Generated by magic
BOOTPROTO='static'
BROADCAST=''
ETHTOOL_OPTIONS=''
IPADDR_4=${IP_AND_PREFIX_LEN}
IPADDR_6=${IP6_PREFIX}
MTU=''
NAME=''
NETMASK=''
NETWORK=''
REMOTE_IPADDR=''
STARTMODE='auto'
DHCLIENT_SET_DEFAULT_ROUTE='yes'
ZONE='public'

DEVEOF

cat > /etc/sysconfig/network/ifroute-${DEV} << DEVEOF
default $GW - ${DEV}
default $GW6 - ${DEV}
DEVEOF

cat > /etc/resolv.conf << DEVEOF
nameserver $GW6
nameserver $GW
DEVEOF

fi



