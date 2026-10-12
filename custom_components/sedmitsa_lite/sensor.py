"""Day type, next day off and next working day."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .bgcalendar import DayKind
from .entity import SedmitsaEntity
from .runtime import SedmitsaConfigEntry


async def async_setup_entry(
    hass: HomeAssistant, entry: SedmitsaConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities(
        [
            DayTypeSensor(entry, "day_type"),
            NextDayOffSensor(entry, "next_day_off"),
            NextWorkingDaySensor(entry, "next_working_day"),
        ]
    )


class DayTypeSensor(SedmitsaEntity, SensorEntity):
    """Today's kind of day."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [k.value for k in DayKind]

    @property
    def native_value(self) -> str:
        return self.data.calendar.day(self.data.today()).kind.value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        day = self.data.calendar.day(self.data.today())
        return {"date": day.date.isoformat(), "name": day.name(self.data.language), "working_day": day.is_working}


class NextDayOffSensor(SedmitsaEntity, SensorEntity):
    """The next holiday or other day off that is not an ordinary weekend."""

    _attr_device_class = SensorDeviceClass.DATE

    def _day(self):
        return self.data.calendar.next_day_off(self.data.today() + timedelta(days=1))

    @property
    def native_value(self) -> date:
        return self._day().date

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        day = self._day()
        # The whole block of days off this one starts (holiday plus weekend).
        end = day.date
        while not self.data.calendar.is_working_day(end + timedelta(days=1)):
            end += timedelta(days=1)
        start = day.date
        while not self.data.calendar.is_working_day(start - timedelta(days=1)):
            start -= timedelta(days=1)
        return {
            "name": day.name(self.data.language),
            "kind": day.kind.value,
            "days_until": (day.date - self.data.today()).days,
            "break_start": start.isoformat(),
            "break_end": end.isoformat(),
            "break_days": (end - start).days + 1,
        }


class NextWorkingDaySensor(SedmitsaEntity, SensorEntity):
    """The first working day after today."""

    _attr_device_class = SensorDeviceClass.DATE

    @property
    def native_value(self) -> date:
        return self.data.calendar.next_working_day(self.data.today())

