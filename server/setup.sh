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
sysctl -p /etc/sysctl.d/forward.conf

#Configure Firewall
/usr/sbin/nft flush ruleset
cp $SPATH/templates/nftables.template $SPATH/config/nftables.conf
sed -i -e "s/%CLIENT_NET%/$CLIENT_NET/g" $SPATH/config/nftables.conf
sed -i -e "s/%SERVER_INTERFACE%/$SERVER_INTERFACE/g" $SPATH/config/nftables.conf
cp $SPATH/config/nftables.conf /etc/nftables.conf
/usr/sbin/nft -f nftables.conf

#Get server Public IP
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
echo "###################"
echo ""
read -p "Set VPN password: " password

#Configure VPN
cp $SPATH/templates/swanctl.template $SPATH/config/swanctl.conf
sed -i -e "s/%pw%/$password/g" $SPATH/config/swanctl.conf
sed -i -e "s/%IP%/$IP/g" $SPATH/config/swanctl.conf
cp $SPATH/config/swanctl.conf /etc/swanctl/swanctl.conf
cp $SPATH/config/charon-systemd.conf /etc/strongswan.d/charon-systemd.conf

cp $SPATH/templates/cert.template $SPATH/config/cert.conf
sed -i -e "s/%IP%/$IP/g" $SPATH/config/cert.conf

#Certificate Config
openssl req -x509 -newkey rsa:4096 -keyout $SPATH/key.pem -out $SPATH/cert.pem -sha256 -days 3650 -nodes -config $SPATH/config/cert.conf

mv $SPATH/key.pem /etc/swanctl/private/key.pem
mv $SPATH/cert.pem /etc/swanctl/x509/cert.pem

systemctl restart strongswan
systemctl enable strongswan

