"""Calendar of holidays and days off."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .bgcalendar import MAX_YEAR, MIN_YEAR
from .entity import SedmitsaEntity
from .runtime import SedmitsaConfigEntry

LOOKAHEAD = 400


async def async_setup_entry(
    hass: HomeAssistant, entry: SedmitsaConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([HolidayCalendar(entry, "holidays")])


def _as_date(value: datetime | date) -> date:
    return value.date() if isinstance(value, datetime) else value


def _last_date(end: datetime | date) -> date:
    """The last whole day before an exclusive end (HA passes [start, end))."""
    if isinstance(end, datetime):
        return (end - timedelta(microseconds=1)).date()
    return end - timedelta(days=1)


class HolidayCalendar(SedmitsaEntity, CalendarEntity):
    """Official holidays, moved and declared days off."""

    def _events(self, start: date, end: date) -> list[CalendarEvent]:
        lang = self.data.language
        out = []
        for day in self.data.calendar.special_days(start, end):
            out.append(
                CalendarEvent(
                    start=day.date,
                    end=day.date + timedelta(days=1),
                    summary=day.name(lang),
                    description=day.kind.value,
                    uid=f"sedmitsa-lite-{day.date.isoformat()}",
                )
            )
        return out

    @property
    def event(self) -> CalendarEvent | None:
        today = self.data.today()
        events = self._events(today, today + timedelta(days=LOOKAHEAD))
        return events[0] if events else None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        start = max(_as_date(start_date), date(MIN_YEAR, 1, 1))
        end = min(_last_date(end_date), date(MAX_YEAR, 12, 31))
        if end < start:
            return []
        return self._events(start, end)

