#!/usr/bin/env bash

set -e

[ $EUID -ne 0 ] && echo "run as root" >&2 && exit 1

apt update && \
  DEBIAN_FRONTEND=noninteractive apt install -y \
    dnsmasq netfilter-persistent iptables-persistent

# Create and persist iptables rule.
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 172.16.0.1:80
sudo iptables -t nat -A PREROUTING -p tcp --dport 554 -j DNAT --to-destination 172.16.0.1:554
sudo iptables -t nat -A PREROUTING -p tcp --dport 1935 -j DNAT --to-destination 172.16.0.1:1935
netfilter-persistent save
sudo sed -i'' s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/ /etc/sysctl.conf

# Static IP for eth0
cat <<'EOF' >/etc/dhcpcd.conf
interface eth0
static ip_address=172.16.0.2
EOF

# Create a dnsmasq DHCP config at /etc/dnsmasq.d/bridge.conf. The Raspberry Pi
# will act as a DHCP server to the client connected over ethernet.
cat <<'EOF' >/etc/dnsmasq.conf
interface=eth0
bind-dynamic
domain-needed
bogus-priv
dhcp-range=172.16.0.2,172.16.0.3,255.255.255.254,12h
EOF

systemctl mask networking.service
sudo reboot now