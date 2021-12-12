<!--
SPDX-FileCopyrightText: 2021 The ha-octopus-energy Authors

SPDX-License-Identifier: Apache-2.0
-->

# Home Assistant/Octopus Energy Integration

This is a very _very_ rough implementation at the time of writing. Pull requests welcome.

**Minimum supported version of Home Assistant is 2021.12.**

This integration provides the ability to request [Octopus Energy](https://share.octopus.energy/wheat-ram-24)
for consumption and tariff information for electricity meter points.

The integration requires you to provide the API key and the account number, that can be retrieved
from the «Developer Settings» page under «Personal Information».

Electricity consumption is exposed individually for each meter identified in the account. Tariff data is
exposed for each MPRN (meter point, supply) identified in the account.

## Limitations

This integration is fairly rough, and should be considered an early stage work in progress.

As part of the limitation of the API, consumption data is only updated once per day, with the consumption of
the previous day (midnight-to-midnight). It is known for consumption data to be delayed, which can cause the
usage to be reported "spiky", despite Octopus Energy providing a granularity of half an hour on the readings.

Because of this lack of granularity, tariff information is only reliable for fixed tariffs, and the sensor is
only implemented for Standard Tariffs right now.

Gas supplies are not currently reported. This is because I have no access to that information to make sure it
works correctly.

## Note on logs

The default logs for the `gql` transport are very verbose at `info` level (the default for Home Assistant),
logging each request and response.

I would recommend you update your configuration to raise the verbosity of the transport:

```
logger:
  default: info
  logs:
    gql.transport.aiohttp: warning
```
