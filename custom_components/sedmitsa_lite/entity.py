"""Base entity for Sedmitsa Lite."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SIGNAL_NEW_DAY
from .runtime import SedmitsaConfigEntry, SedmitsaData


class SedmitsaEntity(Entity):
    """Shares the device, the calendar and the midnight refresh."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry: SedmitsaConfigEntry, key: str) -> None:
        self.entry = entry
        self.data: SedmitsaData = entry.runtime_data
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="PN Scripts",
            model="Bulgarian working-day calendar",
            sw_version="1.0.0",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://pnscripts.com/marketplace/ha-sedmitsa",
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{SIGNAL_NEW_DAY}_{self.entry.entry_id}", self.async_write_ha_state
            )
        )
