# SPDX-FileCopyrightText: 2021 The ha-octopus-energy Authors
#
# SPDX-License-Identifier: Apache-2.0

from typing import Mapping, Optional, Tuple

from async_timeout import timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from octopy_energy import Consumption, Tariff, graphql

from .const import CONF_ACCOUNT_NUMBER, CONF_API_KEY, DOMAIN

PLATFORMS = ["sensor"]


class OctopusEnergyAccountState:
    _api_key: str
    _account_number: str
    last_result: Optional[Mapping[str, Tuple[Mapping[str, Consumption], Tariff]]]

    def __init__(self, api_key: str, account_number: str) -> None:
        self._api_key = api_key
        self._account_number = account_number
        self.last_result = None

    async def fetch_data(
        self,
    ) -> Optional[Mapping[str, Tuple[Mapping[str, Consumption], Tariff]]]:
        async with timeout(10):
            async with graphql.ClientSession(self._api_key) as session:
                self.last_result = await session.query_account_current_electricity_consumption_and_tariff(
                    self._account_number
                )
                return self.last_result


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    assert entry.unique_id is not None

    api_key = entry.data[CONF_API_KEY]
    account_number = entry.data[CONF_ACCOUNT_NUMBER]
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = OctopusEnergyAccountState(
        api_key, account_number
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
