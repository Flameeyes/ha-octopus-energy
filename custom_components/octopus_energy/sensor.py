# SPDX-FileCopyrightText: 2021 The ha-octopus-energy Authors
#
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import timedelta
from typing import Any, Mapping

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENERGY_KILO_WATT_HOUR, ENERGY_MEGA_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from octopy_energy import Consumption, Tariff

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:

    state = hass.data[DOMAIN][entry.entry_id]

    # 15 minutes delay because updates happen at best every half hour!
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="octopus_energy.sensor",
        update_method=state.fetch_data,
        update_interval=timedelta(minutes=15),
    )

    await coordinator.async_config_entry_first_refresh()

    entities = []

    for mpan, (consumptions, _) in coordinator.data.items():
        entities.append(OctopusEnergyTariffSensorEntity(coordinator, mpan))
        entities.extend(
            OctopusEnergyConsumptionSensorEntity(coordinator, mpan, meter_serial)
            for meter_serial in consumptions.keys()
        )

    if entities:
        async_add_entities(entities, True)


class OctopusEnergyTariffSensorEntity(CoordinatorEntity, SensorEntity):

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT

    _mpan: str

    def __init__(self, coordinator, mpan):
        super().__init__(coordinator)
        self._mpan = mpan

    @property
    def name(self) -> str:
        return f"{self._mpan} Tariff"

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}-tariff-{self._mpan}"

    @property
    def tariff(self) -> Tariff:
        return self.coordinator.data[self._mpan][1]

    @property
    def native_value(self) -> float:
        # We report the value in GBP/MWh because it provides more resolution than the
        # GBp/kWh that otherwise rounds down to zero.
        return f"{self.tariff.rate * 10:.2f}"

    @property
    def unit_of_measurement(self) -> str:
        return f"GBP/{ENERGY_MEGA_WATT_HOUR}"

    @property
    def device_info(self) -> Mapping[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._mpan)},
            "default_name": "Electricity Meter Point",
        }


class OctopusEnergyConsumptionSensorEntity(CoordinatorEntity, SensorEntity):

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    _mpan: str
    _meter_serial: str

    def __init__(self, coordinator, mpan, meter_serial):
        super().__init__(coordinator)
        self._mpan = mpan
        self._meter_serial = meter_serial

    @property
    def name(self) -> str:
        return f"{self._meter_serial} Consumption"

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}-consumption-{self._meter_serial}"

    @property
    def consumption(self) -> Consumption:
        return self.coordinator.data[self._mpan][0][self._meter_serial]

    @property
    def native_value(self) -> str:
        return str(self.consumption.consumption)

    @property
    def device_info(self) -> Mapping[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._meter_serial)},
            "via_device": (DOMAIN, self._mpan),
            "default_name": "Electricity Meter",
        }
