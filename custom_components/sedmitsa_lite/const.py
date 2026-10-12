"""Constants for Sedmitsa Lite by PN Scripts."""

from __future__ import annotations

DOMAIN = "sedmitsa_lite"
DEFAULT_NAME = "Sedmitsa Lite"

CONF_WORKDAYS = "workdays"
CONF_ENLIGHTENERS = "enlighteners_day_off"
CONF_DECLARED = "use_declared_days"
CONF_NAMES_LANGUAGE = "names_language"

LANG_AUTO = "auto"

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

DEFAULTS = {
    CONF_WORKDAYS: ["mon", "tue", "wed", "thu", "fri"],
    CONF_ENLIGHTENERS: False,
    CONF_DECLARED: True,
    CONF_NAMES_LANGUAGE: LANG_AUTO,
}

SIGNAL_NEW_DAY = f"{DOMAIN}_new_day"
