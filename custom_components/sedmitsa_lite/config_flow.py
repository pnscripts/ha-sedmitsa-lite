"""UI setup and options for Sedmitsa Lite."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

try:
    import probatio as vol
except ImportError:  # pragma: no cover
    import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.selector import BooleanSelector, SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import CONF_DECLARED, CONF_ENLIGHTENERS, CONF_NAMES_LANGUAGE, CONF_WORKDAYS, DEFAULT_NAME, DEFAULTS, DOMAIN, LANG_AUTO, WEEKDAYS


def options_schema(values: Mapping[str, Any]) -> vol.Schema:
    v = {**DEFAULTS, **values}
    return vol.Schema(
        {
            vol.Required(CONF_WORKDAYS, default=v[CONF_WORKDAYS]): SelectSelector(
                SelectSelectorConfig(options=WEEKDAYS, multiple=True, translation_key="weekday", mode=SelectSelectorMode.DROPDOWN)
            ),
            vol.Required(CONF_DECLARED, default=v[CONF_DECLARED]): BooleanSelector(),
            vol.Required(CONF_ENLIGHTENERS, default=v[CONF_ENLIGHTENERS]): BooleanSelector(),
            vol.Required(CONF_NAMES_LANGUAGE, default=v[CONF_NAMES_LANGUAGE]): SelectSelector(
                SelectSelectorConfig(options=[LANG_AUTO, "bg", "en"], translation_key="names_language")
            ),
        }
    )


def validate(user_input: dict[str, Any]) -> dict[str, str]:
    return {} if user_input.get(CONF_WORKDAYS) else {CONF_WORKDAYS: "no_workdays"}


class SedmitsaLiteConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add a Sedmitsa Lite calendar."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            name = (user_input.pop(CONF_NAME, "") or DEFAULT_NAME).strip()
            errors = validate(user_input)
            if not errors:
                await self.async_set_unique_id(name.casefold())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=name, data={}, options=user_input)
            user_input[CONF_NAME] = name
        schema = vol.Schema(
            {vol.Required(CONF_NAME, default=(user_input or {}).get(CONF_NAME, DEFAULT_NAME)): str}
        ).extend(options_schema(user_input or {}).schema)
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> SedmitsaLiteOptionsFlow:
        return SedmitsaLiteOptionsFlow()


class SedmitsaLiteOptionsFlow(OptionsFlow):
    """Change the settings of an existing calendar."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = validate(user_input)
            if not errors:
                return self.async_create_entry(data=user_input)
        current = user_input or {**DEFAULTS, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=options_schema(current), errors=errors)
