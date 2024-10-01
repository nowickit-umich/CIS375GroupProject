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
nft list ruleset > /etc/nftables.conf

#Configure VPN
curl -o /etc/swanctl/swanctl.conf https://raw.githubusercontent.com/nowickit-umich/CIS375GroupProject/refs/heads/main/server/config/swanctl.conf

#VPN Certificate config
#TODO
curl -o /root/ca.conf https://raw.githubusercontent.com/nowickit-umich/CIS375GroupProject/refs/heads/main/server/config/cert/ca.conf
curl -o /root/server.conf https://raw.githubusercontent.com/nowickit-umich/CIS375GroupProject/refs/heads/main/server/config/cert/server.conf

openssl rand 19 > /root/serial
openssl genpkey -algorithm RSA -out /root/ca-key.pem -pkeyopt rsa_keygen_bits:4096
openssl req -x509 -new -noenc -key ca-key.pem -sha256 -days 3650 -out /etc/swanctl/x509ca/ca-cert.pem -config /root/ca.conf
openssl genpkey -algorithm RSA -out /etc/swanctl/private/server-key.pem -pkeyopt rsa_keygen_bits:4096
openssl req -new -key /etc/swanctl/private/server-key.pem -outform pem -out server-req.pem
openssl ca -in server-req.pem -inform pem -config server.conf

systemctl restart strongswan
systemctl enable strongswan


#Web server setup

