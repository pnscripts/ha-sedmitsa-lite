"""Per-entry state for Sedmitsa Lite: the calendar built from the entry's options."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .bgcalendar import BulgarianCalendar, Settings
from .const import CONF_DECLARED, CONF_ENLIGHTENERS, CONF_NAMES_LANGUAGE, CONF_WORKDAYS, DEFAULTS, LANG_AUTO, WEEKDAYS

type SedmitsaConfigEntry = ConfigEntry[SedmitsaData]


def merged_options(entry: ConfigEntry) -> dict[str, Any]:
    """Defaults, then the entry's data, then its options."""
    return {**DEFAULTS, **entry.data, **entry.options}


def build_settings(options: Mapping[str, Any]) -> Settings:
    return Settings(
        workdays=frozenset(WEEKDAYS.index(d) for d in options[CONF_WORKDAYS]),
        enlighteners_day_off=bool(options[CONF_ENLIGHTENERS]),
        use_declared_days=bool(options[CONF_DECLARED]),
    )


@dataclass(slots=True)
class SedmitsaData:
    """What the platforms of one entry share."""

    hass: HomeAssistant
    calendar: BulgarianCalendar
    names_language: str

    @classmethod
    def from_entry(cls, hass: HomeAssistant, entry: ConfigEntry) -> SedmitsaData:
        options = merged_options(entry)
        return cls(hass, BulgarianCalendar(build_settings(options)), options[CONF_NAMES_LANGUAGE])

    @property
    def language(self) -> str:
        if self.names_language != LANG_AUTO:
            return self.names_language
        return "bg" if (self.hass.config.language or "").startswith("bg") else "en"

    def today(self) -> date:
        return dt_util.now().date()
