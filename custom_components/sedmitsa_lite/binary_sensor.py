"""Working-day binary sensors."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import SedmitsaEntity
from .runtime import SedmitsaConfigEntry


async def async_setup_entry(
    hass: HomeAssistant, entry: SedmitsaConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([WorkingDaySensor(entry, "working_today", 0), WorkingDaySensor(entry, "working_tomorrow", 1)])


class WorkingDaySensor(SedmitsaEntity, BinarySensorEntity):
    """On when the day is a working day."""

    def __init__(self, entry: SedmitsaConfigEntry, key: str, offset: int) -> None:
        super().__init__(entry, key)
        self.offset = offset

    def _day(self):
        return self.data.calendar.day(self.data.today() + timedelta(days=self.offset))

    @property
    def is_on(self) -> bool:
        return self._day().is_working

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        day = self._day()
        return {"date": day.date.isoformat(), "kind": day.kind.value, "name": day.name(self.data.language)}

