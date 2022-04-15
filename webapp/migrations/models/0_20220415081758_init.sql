-- upgrade --
CREATE TABLE IF NOT EXISTS "policy_rule_list" (
    "instance_id" CHAR(36) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(32) NOT NULL
) /* Policy Rule List */;
CREATE TABLE IF NOT EXISTS "ipv4_filter_rules" (
    "instance_id" CHAR(36) NOT NULL  PRIMARY KEY,
    "src_network" VARCHAR(64) NOT NULL  DEFAULT '0.0.0.0/0',
    "dst_network" VARCHAR(64) NOT NULL  DEFAULT '0.0.0.0/0',
    "except_src" INT NOT NULL  DEFAULT 0,
    "except_dst" INT NOT NULL  DEFAULT 0,
    "protocol" VARCHAR(8)   /* TCP: tcp\nUDP: udp */,
    "action" VARCHAR(8) NOT NULL  DEFAULT 'DROP' /* DROP: DROP\nACCEPT: ACCEPT */,
    "table" VARCHAR(8) NOT NULL  DEFAULT 'FORWARD' /* INPUT: INPUT\nFORWARD: FORWARD */,
    "dst_port_number" INT,
    "policy_rule_list_id" CHAR(36) REFERENCES "policy_rule_list" ("instance_id") ON DELETE CASCADE
) /* Model for a IPv4 Filter Rule */;
CREATE TABLE IF NOT EXISTS "ipv4_nat_rules" (
    "instance_id" CHAR(36) NOT NULL  PRIMARY KEY,
    "target_interface" VARCHAR(32) NOT NULL  DEFAULT 'eth0',
    "policy_rule_list_id" CHAR(36) REFERENCES "policy_rule_list" ("instance_id") ON DELETE CASCADE
) /* NAT rule for a defined interface (always POSTROUTING with MASQUERADE) */;
CREATE TABLE IF NOT EXISTS "ipv6_filter_rules" (
    "instance_id" CHAR(36) NOT NULL  PRIMARY KEY,
    "src_network" VARCHAR(64) NOT NULL  DEFAULT '::/0',
    "dst_network" VARCHAR(64) NOT NULL  DEFAULT '::/0',
    "except_src" INT NOT NULL  DEFAULT 0,
    "except_dst" INT NOT NULL  DEFAULT 0,
    "protocol" VARCHAR(8)   /* TCP: tcp\nUDP: udp */,
    "action" VARCHAR(8) NOT NULL  DEFAULT 'DROP' /* DROP: DROP\nACCEPT: ACCEPT */,
    "table" VARCHAR(8) NOT NULL  DEFAULT 'FORWARD' /* INPUT: INPUT\nFORWARD: FORWARD */,
    "dst_port_number" INT,
    "policy_rule_list_id" CHAR(36) REFERENCES "policy_rule_list" ("instance_id") ON DELETE CASCADE
) /* Model for a IPv6 Filter Rule */;
CREATE TABLE IF NOT EXISTS "ipv6_nat_rules" (
    "instance_id" CHAR(36) NOT NULL  PRIMARY KEY,
    "target_interface" VARCHAR(32) NOT NULL  DEFAULT 'eth0',
    "policy_rule_list_id" CHAR(36) REFERENCES "policy_rule_list" ("instance_id") ON DELETE CASCADE
) /* NAT rule for a defined interface (always POSTROUTING with MASQUERADE) */;
CREATE TABLE IF NOT EXISTS "wg_interfaces" (
    "instance_id" CHAR(36) NOT NULL  PRIMARY KEY,
    "intf_name" VARCHAR(32) NOT NULL UNIQUE /* wireguard interface name */,
    "description" VARCHAR(2048)   DEFAULT '' /* description within the wireguard configuration */,
    "listen_port" INT NOT NULL UNIQUE DEFAULT 51820 /* port number that should be used */,
    "private_key" VARCHAR(64) NOT NULL  /* private key of the interface */,
    "table" VARCHAR(8) NOT NULL  DEFAULT 'auto' /* OFF: off\nAUTO: auto */,
    "cidr_addresses" VARCHAR(2048) NOT NULL  /* comma separated list of IPv4\/IPv6 addresses that are used on the wireguard interface */,
    "policy_rule_list_id" CHAR(36) REFERENCES "policy_rule_list" ("instance_id") ON DELETE SET NULL /* associated interface policy */
) /* Wireguard Interface Data Model */;
CREATE TABLE IF NOT EXISTS "wg_peers" (
    "instance_id" CHAR(36) NOT NULL  PRIMARY KEY,
    "public_key" VARCHAR(64) NOT NULL  /* public key of the peer */,
    "friendly_name" VARCHAR(64),
    "description" VARCHAR(2048)   DEFAULT '',
    "persistent_keepalives" INT   DEFAULT -1,
    "preshared_key" VARCHAR(64)   /* optional preshared key */,
    "endpoint" VARCHAR(64)   /* optional endpoint to connect to the service */,
    "cidr_routes" VARCHAR(2048) NOT NULL  /* comma separated list of IPv4\/IPv6 for the client */,
    "wg_interface_id" CHAR(36) NOT NULL REFERENCES "wg_interfaces" ("instance_id") ON DELETE CASCADE
) /* Wireguard Peer Data Model */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSON NOT NULL
);
