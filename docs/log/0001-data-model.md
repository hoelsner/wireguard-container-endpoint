# Data Model for the Application

* Status: proposed
* Date: 2022-01-29

## Context and Problem Statement

To provide a configuration interface for Wireguard, a data model is required to support the [defined usage scenarios](../scenarios.md).

## Considered Options

* [option 1] use the WireGuard and iptables configuration from the Server and provide an interface to this data
* [option 2] use a data model on-top of the server configuration and generate the specific configuration information for WireGuard and iptables

## Decision Outcome

The use of [option 2] for the Application is preferred because the available configuration options are reduced to the required options for the two scenarios that should be addressed. Furthermore, it is simpler to use/implement because not all options from the underlying tools must be exposed to the configuration interface on day 1.

This makes the application more complex because a mechanism to save the data model and an on-demand translation to the Wireguard/iptables configuration is required. Within this context, the following data model is proposed for the Application.

![Data Model](0001-data-model/model.drawio.svg)

## Links <!-- optional -->

* [Target Sceanrios for the Application](../scenarios/README.md)
