<!--
SPDX-FileCopyrightText: 2021 The ha-octopus-energy Authors

SPDX-License-Identifier: Apache-2.0
-->
# Home Assistant/Octopus Energy Integration

This is a very _very_ rough implementation at the time of writing. Pull requests welcome.

## Note on logs

The default logs for the `gql` transport are very verbose at `info` level (the default for Home
Assistant), logging each request and response.

I would recommend you update your configuration to raise the verbosity of the transport:

```
logger:
  default: info
  logs:
    gql.transport.aiohttp: warning
```
