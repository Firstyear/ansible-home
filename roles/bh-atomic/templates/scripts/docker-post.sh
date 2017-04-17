#!/bin/sh


docker network create -d bridge --gateway={{ docker_v6_prefix }}::1 --subnet={{ docker_v6_prefix }}::/64 --ip-range={{ docker_v6_prefix }}:1::/80 --ipv6 v6br

