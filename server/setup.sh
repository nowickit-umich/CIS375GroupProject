#!/bin/bash
#
#VPN server setup
#Run as root

CLIENT_NET="10.99.99.0\/24"
SERVER_INTERFACE=$(ip -o link show | awk -F': ' '!/lo/ {print $2; exit}')
LOCAL_ADDR=$(hostname -I)
SPATH=$(dirname $(realpath "$0"))

#Install VPN software
apt update
apt install curl charon-systemd strongswan-swanctl libcharon-extra-plugins dnsmasq -y
apt remove strongswan-starter strongswan-charon -y

#Setup DNS
systemctl disable systemd-resolved
systemctl stop systemd-resolved
cp $SPATH/templates/dnsmasq.template $SPATH/config/dnsmasq.conf
sed -i -e "s/%SERVER_INTERFACE%/$SERVER_INTERFACE/g" $SPATH/config/dnsmasq.conf
cp $SPATH/config/dnsmasq.conf /etc/dnsmasq.d/dnsmasq.conf
systemctl enable dnsmasq
systemctl restart dnsmasq

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
/usr/sbin/nft -f /etc/nftables.conf

#Get server Public IP
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 120"`
IP=`curl http://169.254.169.254/latest/meta-data/public-ipv4 -H "X-aws-ec2-metadata-token: $TOKEN"`

# Generate password
password=$(openssl rand -base64 30 | tr -d "/+")
echo "$password" > /home/ubuntu/vpnkey.secret
chmod 664 /home/ubuntu/vpnkey.secret

#Configure VPN
cp $SPATH/templates/swanctl.template $SPATH/config/swanctl.conf
sed -i -e "s/%PW%/"$password"/g" $SPATH/config/swanctl.conf
sed -i -e "s/%IP%/$IP/g" $SPATH/config/swanctl.conf
sed -i -e "s/%CLIENT_NET%/$CLIENT_NET/g" $SPATH/config/swanctl.conf
sed -i -e "s/%LOCAL_ADDR%/$LOCAL_ADDR/g" $SPATH/config/swanctl.conf
cp $SPATH/config/swanctl.conf /etc/swanctl/swanctl.conf
cp $SPATH/config/charon-systemd.conf /etc/strongswan.d/charon-systemd.conf

#Certificate Config
cp $SPATH/templates/cert.template $SPATH/config/cert.conf
sed -i -e "s/%IP%/$IP/g" $SPATH/config/cert.conf
openssl req -x509 -newkey rsa:4096 -keyout $SPATH/key.pem -out $SPATH/cert.pem -sha256 -days 1 -nodes -config $SPATH/config/cert.conf
mv $SPATH/key.pem /etc/swanctl/private/key.pem
mv $SPATH/cert.pem /etc/swanctl/x509/cert.pem

# start server_cmd service
cp $SPATH/server_cmd.py /usr/bin/server_cmd.py
chmod 755 /usr/bin/server_cmd.py
cp $SPATH/systemd/server_cmd.service /etc/systemd/system/
systemctl daemon-reload
systemctl start server_cmd
systemctl enable server_cmd

#Start VPN
systemctl restart strongswan
systemctl enable strongswan
