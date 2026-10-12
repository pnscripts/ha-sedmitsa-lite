"""Sedmitsa Lite by PN Scripts: Bulgarian working days and holidays.

Copyright (c) 2026 ПН СКРИПТС ЕООД / PN Scripts. MIT licence. https://pnscripts.com
"""

from __future__ import annotations

from datetime import datetime

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_change

from .const import DOMAIN, SIGNAL_NEW_DAY
from .runtime import SedmitsaConfigEntry, SedmitsaData

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: SedmitsaConfigEntry) -> bool:
    """Set up one Sedmitsa Lite calendar."""
    entry.runtime_data = SedmitsaData.from_entry(hass, entry)

    @callback
    def new_day(now: datetime) -> None:
        async_dispatcher_send(hass, f"{SIGNAL_NEW_DAY}_{entry.entry_id}")

    entry.async_on_unload(async_track_time_change(hass, new_day, hour=0, minute=0, second=1))
    entry.async_on_unload(entry.add_update_listener(_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _reload(hass: HomeAssistant, entry: SedmitsaConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: SedmitsaConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
