#!/bin/bash
apt-get update
apt-get install -y wireguard

cat <<EOF > /etc/wireguard/wg0.conf
[Interface]
Address = 20.0.0.4/24
ListenPort = 51820
PrivateKey = ${wireguard_private_key}

[Peer]
PublicKey = ${wireguard_peer_public_key}
AllowedIPs = 20.0.0.0/24
Endpoint = 40.76.140.125:51820
PersistentKeepalive = 25
EOF

chmod 600 /etc/wireguard/wg0.conf
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
