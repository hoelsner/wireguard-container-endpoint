# Scenario 1 (Hub-and-Spoke Remote Access) - Manual Configuration

The following configuration is required together with the `docker-compose.yaml` file within this directory.

```bash
cd docs/scenarios/scenario_1
docker-compose build --pull
docker-compose up
```

## Wireguard Hub

```bash
$ docker exec -it scenario_1_wireguard_hub_1 /bin/bash

# create configuration
cat <<EOF > /etc/wireguard/wg16.conf
[Interface]
Address = 172.29.1.1/32, FD00:1::1/128
ListenPort = 51820
PrivateKey = 4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=

# INPUT for traffic to this container, FORWARD for routed traffic
#PostUp =   iptables -A INPUT -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
#PostDown = iptables -D INPUT -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
#PostUp   = ip6tables -A INPUT -i %i -p tcp --dport 1:1023 -s FD00:1::0:/112 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
#PostDown = ip6tables -D INPUT -i %i -p tcp --dport 1:1023 -s FD00:1::0:/112 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp =   iptables -A FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -A FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -p tcp --dport 1:1023 -s 172.29.1.0/24 ! -d 172.29.0.0/24 -j DROP; iptables -D FORWARD -i %i -p tcp --dport 8888 -s 172.29.1.0/24 -d 172.29.0.0/24 -j DROP; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp =   ip6tables -A FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::0:0/112 -j DROP; ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = ip6tables -D FORWARD -i %i -p tcp --dport 1:1023 -s FD00:1::/64 ! -d FD00::0:0/112 -j DROP; ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=
PresharedKey = V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=
AllowedIPs = 172.29.1.16/32, FD00:1::16/128
EOF

# the following command starts wireguard based on a configuration file located at /etc/wireguard/wg16.conf
$ wg-quick up wg16

# shutdown interface
$ wg-quick down wg16

# troubleshoot iptables with the following commands
iptables -nvxL INPUT
watch iptables -nvL INPUT
```

## Client Configuration

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

## Notes

* handshake occured every 2 minutes by default
