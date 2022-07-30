# API authentication layer

* Status: accepted
* Date: 2022-02-26

## Context and Problem Statement

The admin interface (HTTP API) should not be exposed to the public network, but a basic authentication layer should be added to the application. There are no multi-user or permission requirements. When the instance is created, a random or a predefined account based on the environment configuration should be created to provide initial access to the admin API. This should not affect the authentication of Wireguard endpoints.

## Considered Options

* [option 1] implement a static user authentication for HTTP basic authentication
* [option 2] implement a user database for HTTP basic authentication
* [option 2] implement a token-based authentication with JWT and a local user database
* [option 3] implement a token-based authentication with JWT and OAuth2

## Decision Outcome

[option 1] is selected because it doesn't introduce an external dependency for authentication and is easy to implement.
