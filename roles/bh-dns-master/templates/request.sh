# https_proxy=http://proxy-bne1.net.blackhats.net.au:3128 certbot certonly --staging -m william@blackhats.net.au --manual --preferred-challenges=dns --manual-public-ip-logging-ok --agree-tos --manual-auth-hook /root/manual-hook.sh -d testdelete.cloud.blackhats.net.au