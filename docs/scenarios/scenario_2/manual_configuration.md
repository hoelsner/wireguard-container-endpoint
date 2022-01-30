# Scenario 2 (Partial Mesh with Multiple Temporary Hubs) - Manual Configuration

The following configuration is required together with the `docker-compose.yaml` file within this directory.

```bash
cd docs/scenarios/scenario_2
docker-compose build --pull
docker-compose up
```

## Wireguard Hub 1

```bash
$ docker exec -it scenario_2_wireguard_hub_1_1 /bin/bash

# create configuration
cat <<EOF > /etc/wireguard/wg16.conf
[Interface]
Address = 172.29.1.1/32, FD00:1::1/128
ListenPort = 51820
PrivateKey = 4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=

# INPUT for traffic to this container, FORWARD for routed traffic
#PostUp =   iptables -A INPUT -i %i -p tcp --dport 1:1023 -s 172.29.1.1/32 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
#PostDown = iptables -D INPUT -i %i -p tcp --dport 1:1023 -s 172.29.1.1/32 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
#PostUp   = ip6tables -A INPUT -i %i -p tcp --dport 1:1023 -s FD00:1::1/128 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
#PostDown = ip6tables -D INPUT -i %i -p tcp --dport 1:1023 -s FD00:1::1/128 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp =   iptables -A FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -A FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -D FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp =   ip6tables -A FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::/64 -j DROP; ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = ip6tables -D FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::/64 -j DROP; ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Wireguard Client
PublicKey = s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=
PresharedKey = V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=
AllowedIPs = 172.29.1.16/32, FD00:1::16/128
EOF

cat <<EOF > /etc/wireguard/wg15.conf
[Interface]
Address = 172.29.0.241/32, FD00::FFFF:241/128
ListenPort = 51821
PrivateKey = kGv97FqVfHYCioosfTkoWafuWVjwELRziKctegtK6mk=

PostUp =   iptables -A FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -A FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -D FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp =   ip6tables -A FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::/64 -j DROP; ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = ip6tables -D FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::/64 -j DROP; ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Link to Temporary Hub
PublicKey = xY8j0XvlDH80/2XW40SVtdp6yIXBcqhDtu1YHmE3jHI=
PresharedKey = VAh4Pvn05h9BM4wniYGr00FQYu7Lq8tCgh8YpxpaC8Y=
AllowedIPs = 172.29.0.242/32, FD00::FFFF:242/128, 172.29.0.16/28, FD00::1:0/112
EOF

# the following command starts wireguard based on a configuration file located at /etc/wireguard/wg16.conf
$ wg-quick up wg16
$ wg-quick up wg15

# shutdown interface
$ wg-quick down wg16
$ wg-quick down wg15
```

## Wireguard Hub 2

```bash
$ docker exec -it scenario_2_wireguard_hub_2_1 /bin/bash

# create configuration
cat <<EOF > /etc/wireguard/wg16.conf
[Interface]
Address = 172.29.1.2/32, FD00:1::2/128
ListenPort = 51820
PrivateKey = eDXKtwt2kQ5snGee+TpYc4rK5wnYv+W+4Hi4kRJZm1U=
#Table = off

# INPUT for traffic to this container, FORWARD for routed traffic
#PostUp =   iptables -A INPUT -i %i -p tcp --dport 1:1023 -s 172.29.1.1/32 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
#PostDown = iptables -D INPUT -i %i -p tcp --dport 1:1023 -s 172.29.1.1/32 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
#PostUp   = ip6tables -A INPUT -i %i -p tcp --dport 1:1023 -s FD00:1::1/128 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
#PostDown = ip6tables -D INPUT -i %i -p tcp --dport 1:1023 -s FD00:1::1/128 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp =   iptables -A FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -A FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -D FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp =   ip6tables -A FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::/64 -j DROP; ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = ip6tables -D FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::/64 -j DROP; ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Wireguard Client
PublicKey = s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=
PresharedKey = V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=
AllowedIPs = 172.29.1.16/32, FD00:1::16/128
EOF

cat <<EOF > /etc/wireguard/wg15.conf
[Interface]
Address = 172.29.0.241/32, FD00::FFFF:241/128
ListenPort = 51821
PrivateKey = iFcS9ZxSyCzXP5mRPTSJK61Ble7WK52Cg7x3ZJ6zj2I=

PostUp =   iptables -A FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -A FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -D FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp =   ip6tables -A FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::/64 -j DROP; ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = ip6tables -D FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::/64 -j DROP; ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Link to Permanent Hub
PublicKey = h65D5oJpkgS8NQmyBWo2knXb1bHDgw5KCJ72HxczYlY=
PresharedKey = VAh4Pvn05h9BM4wniYGr00FQYu7Lq8tCgh8YpxpaC8Y=
AllowedIPs = 172.29.0.240/28, FD00::FFFF:0/112, 172.29.0.0/24, FD00::/64, 172.29.1.0/24, FD00:1::/64
Endpoint = wireguard_hub_1:51821
PersistentKeepalive = 25
EOF

# the following command starts wireguard based on a configuration file located at /etc/wireguard/wg16.conf
$ wg-quick up wg15
$ wg-quick up wg16

# shutdown interface
$ wg-quick down wg15
$ wg-quick down wg16

# troubleshoot iptables with the following commands
iptables -nvxL INPUT
watch iptables -nvL INPUT
```

## Client Configuration

### Test Indirect Access via Hub 1

```
[Interface]
PrivateKey = sJVz9zldsUb48AtGULMRPTNTF0UfX+XF2AHKtopYLlU=
Address = 172.29.1.16/32, fd00:1::16/128

[Peer]
PublicKey = yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=
PresharedKey = V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=
AllowedIPs = 172.29.0.0/24, 172.29.1.0/24, fd00::/64, fd00:1::/64
Endpoint = 127.0.0.1:51820
PersistentKeepalive = 25
```

### Test Dual Access via Hub 1 and 2

```
[Interface]
PrivateKey = sJVz9zldsUb48AtGULMRPTNTF0UfX+XF2AHKtopYLlU=
Address = 172.29.1.16/32, fd00:1::16/128

[Peer]
PublicKey = yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=
PresharedKey = V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=
AllowedIPs = 172.29.0.0/24, 172.29.1.0/24, fd00::/64, fd00:1::/64
Endpoint = 127.0.0.1:51820
PersistentKeepalive = 25

[Peer]
PublicKey = KMFZz2cUuQx0Equ6ITTJOTt1qB/WFR8C/Yw7oYXsSAE=
PresharedKey = V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=
AllowedIPs = 172.29.0.16/28, fd00::1:0/112
Endpoint = 127.0.0.1:51821
PersistentKeepalive = 25
```

## Notes

* to disable the automatic creation of the routing table use `Table = off` in WireGuard configuration.

```bash
ip -4 route add 172.29.1.16/32 dev wg16
ip -6 route add fd00:1::16/128 dev wg16

ip -4 route remove 172.29.1.16/32 dev wg16
ip -6 route remove fd00:1::16/128 dev wg16
```