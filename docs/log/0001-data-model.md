# Data Model Requirements for the Application

* Status: proposed
* Date: 2022-01-29

## Context and Problem Statement

To provide a configuration interface for WireGuard together with filtering capabilities, a data model is required to support the [defined usage scenarios](../scenarios.md).

## Considered Options

* [option 1] use the WireGuard and iptable configuration from the Server and provide an interface to this data
* [option 2] use a data model on-top of the server configuration and generate the specific configuration information for WireGuard and iptables

## Decision Outcome

The usage of a data model on top of the WireGuard/iptables The usage of an own data model for the Container on top of the WireGuard/iptables configuration is preferred because the available configuration options are reduced to the required options for the scenarios. Furthermore, it is simpler to use/implement because not all options from the underlying tools must be exposed to the interface.

This makes the application more complex because a mechanism to save the data model and an on-demand translation to the WireGuard/iptables configuration is required.

Within this context, the following data model is proposed for the application.

![Data Model](0001-data-model/model.drawio.svg)

## Links <!-- optional -->

* [Description of Scenarios](../scenarios/README.md)
