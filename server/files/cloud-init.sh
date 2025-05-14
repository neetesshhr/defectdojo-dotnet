#!/bin/bash
apt-get update
apt-get install -y wireguard

cat <<EOF > /etc/wireguard/wg0.conf
[Interface]
Address = 20.0.0.4/24
ListenPort = 51820
PrivateKey = YB6eZxWWWGz1D3DqnVQSFE8GMyWmHCFeYxugasVkfGo=


[Peer]
PublicKey = 59+M5AQrC+rg2RxWb3llGHWCfmkeYHgVHn90VXSaUSM=
AllowedIPs = 20.0.0.0/24
Endpoint = 40.76.140.125:51820
PersistentKeepalive = 25
EOF

chmod 600 /etc/wireguard/wg0.conf
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
