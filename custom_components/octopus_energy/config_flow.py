# SPDX-FileCopyrightText: 2021 The ha-octopus-energy Authors
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

import voluptuous as vol
from homeassistant.config_entries import CONN_CLASS_CLOUD_POLL, ConfigFlow
from octopy_energy import graphql

from .const import CONF_ACCOUNT_NUMBER, CONF_API_KEY, DOMAIN


class OctopusEnergyConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, info: Optional[dict] = None):
        errors = {}
        if info is not None:
            apikey = info[CONF_API_KEY]
            account_number = info[CONF_ACCOUNT_NUMBER]

            for entry in self._async_current_entries():
                if entry.unique_id == account_number:
                    return self.async_abort(reason="already_configured")

            await self.async_set_unique_id(account_number)
            self._abort_if_unique_id_configured()

            try:
                async with graphql.ClientSession(apikey) as session:
                    await session.query_account_active_electricity_tariffs(
                        account_number
                    )
            except Exception:
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(
                    title=f"Octopus Energy Account {account_number}",
                    data={CONF_API_KEY: apikey, CONF_ACCOUNT_NUMBER: account_number},
                )

        info = info or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY, default=info.get(CONF_API_KEY, "")): str,
                    vol.Required(
                        CONF_ACCOUNT_NUMBER, default=info.get(CONF_ACCOUNT_NUMBER, "")
                    ): str,
                }
            ),
            errors=errors,
        )
