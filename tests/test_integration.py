"""Sedmitsa Lite inside a real Home Assistant core (pytest-homeassistant-custom-component)."""

from freezegun.api import FrozenDateTimeFactory
import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util

from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.sedmitsa_lite.const import DOMAIN

BASE = {
    "name": "Office",
    "workdays": ["mon", "tue", "wed", "thu", "fri"],
    "use_declared_days": True,
    "enlighteners_day_off": False,
    "names_language": "auto",
}


async def add_entry(hass: HomeAssistant, **changes) -> str:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**BASE, **changes})
    assert result["type"] is FlowResultType.CREATE_ENTRY, result
    await hass.async_block_till_done()
    return result["result"].entry_id


@pytest.fixture
async def office(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> str:
    await hass.config.async_set_time_zone("Europe/Sofia")
    freezer.move_to("2026-12-23 10:00:00+02:00")
    return await add_entry(hass)


async def test_entities_before_christmas(hass: HomeAssistant, office: str) -> None:
    assert hass.states.get("binary_sensor.office_working_day_today").state == "on"
    tomorrow = hass.states.get("binary_sensor.office_working_day_tomorrow")
    assert tomorrow.state == "off"
    assert tomorrow.attributes["kind"] == "public_holiday"
    assert tomorrow.attributes["name"] == "Christmas Eve"
    assert hass.states.get("sensor.office_today").state == "working_day"
    nxt = hass.states.get("sensor.office_next_day_off")
    assert nxt.state == "2026-12-24"
    assert nxt.attributes["days_until"] == 1
    assert nxt.attributes["break_start"] == "2026-12-24"
    assert nxt.attributes["break_end"] == "2026-12-28"
    assert nxt.attributes["break_days"] == 5
    assert hass.states.get("sensor.office_next_working_day").state == "2026-12-29"
    cal = hass.states.get("calendar.office_holidays_and_days_off")
    assert cal.state == "off"
    assert cal.attributes["message"] == "Christmas Eve"
    # Only the Lite entities exist.
    entities = sorted(s.entity_id for s in hass.states.async_all() if s.entity_id.split(".")[1].startswith("office"))
    assert entities == [
        "binary_sensor.office_working_day_today",
        "binary_sensor.office_working_day_tomorrow",
        "calendar.office_holidays_and_days_off",
        "sensor.office_next_day_off",
        "sensor.office_next_working_day",
        "sensor.office_today",
    ]


async def test_midnight_rollover(hass: HomeAssistant, office: str, freezer: FrozenDateTimeFactory) -> None:
    freezer.move_to("2026-12-24 00:00:01+02:00")
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()
    assert hass.states.get("binary_sensor.office_working_day_today").state == "off"
    assert hass.states.get("sensor.office_today").state == "public_holiday"
    assert hass.states.get("calendar.office_holidays_and_days_off").state == "on"
    freezer.move_to("2026-12-28 00:00:01+02:00")
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()
    today = hass.states.get("sensor.office_today")
    assert today.state == "moved_day_off"
    assert today.attributes["name"] == "Day off for Christmas, second day (26.12)"


async def test_bulgarian_names_follow_home_assistant(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    await hass.config.async_set_time_zone("Europe/Sofia")
    hass.config.language = "bg"
    freezer.move_to("2026-12-23 10:00:00+02:00")
    await add_entry(hass)
    assert hass.states.get("binary_sensor.office_working_day_tomorrow").attributes["name"] == "Бъдни вечер"


async def test_calendar_api(hass: HomeAssistant, office: str, hass_client) -> None:
    client = await hass_client()
    resp = await client.get(
        "/api/calendars/calendar.office_holidays_and_days_off?start=2025-12-31T22:00:00Z&end=2026-12-31T22:00:00Z"
    )
    assert resp.status == 200
    events = await resp.json()
    starts = [e["start"]["date"] for e in events]
    assert "2026-01-02" in starts and "2026-12-28" in starts and "2026-04-12" in starts
    assert len(starts) == 18
    assert {e["description"] for e in events} == {"public_holiday", "moved_day_off", "declared_day_off"}
    resp = await client.get("/api/calendars/calendar.office_holidays_and_days_off?start=2200-01-01T00:00:00Z&end=2200-02-01T00:00:00Z")
    assert await resp.json() == []


async def test_config_flow_errors_and_duplicates(hass: HomeAssistant, office: str) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**BASE, "name": "Other", "workdays": []})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"workdays": "no_workdays"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**BASE, "name": "office"})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow_reloads(hass: HomeAssistant, office: str) -> None:
    entry = hass.config_entries.async_get_entry(office)
    result = await hass.config_entries.options.async_init(office)
    assert result["type"] is FlowResultType.FORM
    opts = {k: v for k, v in BASE.items() if k != "name"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {**opts, "workdays": ["mon", "tue"], "names_language": "bg"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    assert hass.states.get("binary_sensor.office_working_day_today").state == "off"  # Wednesday
    assert hass.states.get("binary_sensor.office_working_day_tomorrow").attributes["name"] == "Бъдни вечер"


async def test_unload(hass: HomeAssistant, office: str) -> None:
    assert await hass.config_entries.async_unload(office)
    await hass.async_block_till_done()
    assert hass.config_entries.async_get_entry(office).state is ConfigEntryState.NOT_LOADED


async def test_yaml_is_rejected_gracefully(hass: HomeAssistant) -> None:
    assert await async_setup_component(hass, DOMAIN, {})


async def test_translations_match(hass: HomeAssistant) -> None:
    import json
    from pathlib import Path

    root = Path(__file__).parent.parent / "custom_components" / DOMAIN

    def keys(obj, prefix=""):
        out = set()
        for k, v in obj.items():
            out.add(prefix + k)
            if isinstance(v, dict):
                out |= keys(v, prefix + k + ".")
        return out

    strings = json.loads((root / "strings.json").read_text())
    for lang in ("en", "bg"):
        assert keys(json.loads((root / "translations" / f"{lang}.json").read_text())) == keys(strings), lang
    manifest = json.loads((root / "manifest.json").read_text())
    hacs = json.loads((root.parent.parent / "hacs.json").read_text())
    assert manifest["domain"] == DOMAIN and manifest["version"] and hacs["name"] == "Sedmitsa Lite"
    assert (root / "brand" / "icon.png").exists()
