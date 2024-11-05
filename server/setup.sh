#!/bin/bash
#
#VPN server setup
#Run as root

CLIENT_NET="10.99.99.0/24"
SERVER_INTERFACE="enX0"

SPATH=$(dirname $(realpath "$0"))

#Install VPN software
apt update
apt install curl charon-systemd strongswan-swanctl libcharon-extra-plugins -y
apt remove strongswan-starter strongswan-charon -y

#Enable forwarding
if [ ! -f /etc/sysctl.d/forward.conf ]; then
        echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/forward.conf
fi
#Reload config
sysctl -p

#Configure Firewall
nft flush ruleset
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
nft 'add chain ip filter input { type filter hook input priority 0; policy drop }'
nft add rule ip filter input tcp dport 22 accept
nft add rule ip filter input udp dport 500 accept
nft add rule ip filter input udp dport 4500 accept

#Save Firewall Config
nft list ruleset > /etc/nftables.conf

IP="$(curl -s ifconfig.me)"
if [[ -z "$IP" ]]
then
        IP="$(curl -s ipinfo.io/ip)"
fi
if [[ -z "$IP" ]]
then
        IP="$(curl -s icanhazip.com)"
fi
if [[ -z "$IP" ]]
then
        echo "Failed to get IP"
        exit 1
fi

#Get user input to set password
read -p "Set VPN password: " password

#Configure VPN
cp $SPATH/templates/swanctl.template $SPATH/config/swanctl.conf
sed -i -e "s/%pw%/$password/g" $SPATH/config/swanctl.conf
sed -i -e "s/%IP%/$IP/g" $SPATH/config/swanctl.conf
cp $SPATH/config/swanctl.conf /etc/swanctl/swanctl.conf
cp $SPATH/config/charon-systemd.conf /etc/strongswan.d/charon-systemd.conf

cp $SPATH/templates/cert.template $SPATH/config/certs/cert.conf
sed -i -e "s/%IP%/$IP/g" $SPATH/config/certs/cert.conf

#Certificate Config
openssl req -x509 -newkey rsa:4096 -keyout $SPATH/key.pem -out $SPATH/cert.pem -sha256 -days 3650 -nodes -config $SPATH/config/certs/cert.conf

mv $SPATH/key.pem /etc/swanctl/private/key.pem
mv $SPATH/cert.pem /etc/swanctl/x509/cert.pem

systemctl restart strongswan
systemctl enable strongswan

