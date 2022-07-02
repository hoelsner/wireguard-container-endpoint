# E2E tests

Before running the End-to-End tests for the container, make sure that you installed docker and the development requirements in your python environment. **Please Note:** That the container will reconfigure the wireguard connections several times.

## Run the testcases

To perform automatic E2E testing, go to the `/tests` directory and run the following commands:

```bash
$ cd tests
$ pytest
```

To develop the end-to-end test cases, you can stage the container environment using the following commands:

```bash
# Hub-and-Spoke Scenario 1
$ cd tests
$ export TEST_HOST_IP=127.0.0.1
$ python3 cli.py create-scenario-1
create containers for scenario 1...
containers for scenario 1 created
# destroy it using the following command
$ python3 cli.py destroy-scenario-1
```

```bash
# Partial-Mesh Scenario 2
$ cd tests
$ export TEST_HOST_IP=127.0.0.1
$ python3 cli.py create-scenario-2
create containers for scenario 2...
containers for scenario 2 created
# destroy it using the following command
$ python3 cli.py destroy-scenario-2
```

To change the target URL to connect to the containers, you need to overwrite the IP address using the variable `TEST_HOST_IP` (e.g. `TEST_HOST_IP=192.168.164.38`).

Within the scenarios, a test client on the hub is deployed that can be used with the following wireguard configuration file (e.g. for testing):

```
[Interface]
PrivateKey = 8H/dSh/s2sb1rOUiERJPLci+ggYCWhMaNViTmdC3rX4=
Address = 172.29.1.32/32, fd00:1::32/128

[Peer]
PublicKey = yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=
PresharedKey = VAh4Pvn05h9BM4wniYGr00FQYu7Lq8tCgh8YpxpaC8Y=
AllowedIPs = 172.29.0.0/24, 172.29.1.0/24, fd00::/64, fd00:1::/64
Endpoint = <IP>:51820
```

## Scenario 1 (Hub-and-Spoke) test case

The following diagram describes the structure of the test infrastructure for scenario 1.

![](../docs/scenarios/scenario_1/scenario_1.drawio.svg)

## Scenario 1 (Partial Mesh with Multiple Temporary Hubs) test case

The following diagram describes the structure of the test infrastructure for scenario 2.

![](../docs/scenarios/scenario_2/test_scenario_2.drawio.svg)
