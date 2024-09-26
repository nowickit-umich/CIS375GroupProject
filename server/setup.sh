#!/bin/bash
#
#VPN server setup
#Run as root

CLIENT_NET="10.99.99.0/24"
SERVER_INTERFACE="enX0"

#Install VPN software
apt update
apt install charon-systemd strongswan-swanctl -y
apt remove strongswan-starter strongswan-charon -y

#Enable forwarding
if [ ! -f /etc/sysctl.d/forward.conf ]; then
        echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/forward.conf
fi
#Reload config
sysctl -p

#Configure Firewall
#VPN client NAT
nft add table ip nat
nft 'add chain ip nat postrouting { type nat hook postrouting priority 100; }'
nft add rule ip nat postrouting ip saddr $CLIENT_NET oif $SERVER_INTERFACE masquerade

#Allow traffic from VPN network
nft add table ip filter
nft 'add chain ip filter forward { type filter hook forward priority 0; }'
nft add rule ip filter forward ip saddr $CLIENT_NET accept
nft add rule ip filter forward ct state related,established accept

#Allow VPN server traffic
nft 'add chain ip filter input { type filter hook input priority 0; policy deny }'
nft add rule ip filter input tcp dport 22 accept
nft add rule ip filter input udp dport 500 accept
nft add rule ip filter input udp dport 4500 accept

#Save Firewall Config
#nft list ruleset > /etc/nftables.conf

#Configure VPN
#curl -o /etc/ipsec.conf https://github.com/nowickit-umich/CIS375GroupProject/blob/main/server/config/ipsec.conf

systemctl restart strongswan
systemctl enable strongswan
