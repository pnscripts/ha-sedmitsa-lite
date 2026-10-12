# Sedmitsa Lite by PN Scripts

Free Bulgarian working days and holidays for Home Assistant (MIT). Sedmitsa
Lite knows the official holidays of the Labour Code, moves the days off when
a holiday falls on a weekend and includes the non-working days the
government declares. Everything is computed locally: no cloud, no account,
no API key.

![Sedmitsa Lite entities a day before Christmas](https://raw.githubusercontent.com/pnscripts/sedmitsa-lite/main/listing/entities-1280x720.png)

## Install

- HACS: search for **Sedmitsa Lite** (or add `https://github.com/pnscripts/sedmitsa-lite` as a custom repository of type Integration), install, restart.
- Manual: copy `custom_components/sedmitsa_lite` into your configuration's `custom_components` folder and restart.

Then **Settings > Devices & services > Add integration > Sedmitsa Lite**: give the calendar a name, keep Monday to Friday, submit.

## Entities

| Entity | What it shows |
|--------|---------------|
| `binary_sensor.<name>_working_day_today` / `_tomorrow` | On on a working day. Attributes: `date`, `kind`, `name` |
| `sensor.<name>_today` | `working_day`, `weekend`, `public_holiday`, `moved_day_off` or `declared_day_off` |
| `sensor.<name>_next_day_off` | Date of the next holiday or other day off (ordinary weekends skipped), with `days_until` and the whole break (`break_start`, `break_end`, `break_days`) |
| `sensor.<name>_next_working_day` | The first working day after today |
| `calendar.<name>_holidays_and_days_off` | All holidays and days off as all-day events |

Every entity updates just after midnight. Options: working days of the week,
declared non-working days on or off, 1 November as a day off (schools and
universities), and the language of holiday names (Home Assistant's, Bulgarian
or English).

## Rules

- **Official holidays** (Labour Code, art. 154(1)): 1 January, 3 March, 1 May, 6 May, 24 May, 6 September, 22 September, 24, 25 and 26 December, and Good Friday, Holy Saturday, Easter Sunday and Easter Monday by the Orthodox calendar.
- **Moved days off** (art. 154(2)): a holiday other than Easter on a Saturday or Sunday gives a day off on the first working day after it. Christmas 2026 gives Monday 28 December.
- **Declared non-working days**: 31 December 2025 and 2 January 2026 (Council of Ministers decision of 19 November 2025).
- Covered years: 2013 to 2099.

The full edition, Sedmitsa, adds the school calendar with school-day sensors,
your own extra days off and working days, the monthly working-hours norm and
three actions (count working days, add working days, check a date):
https://pnscripts.com/marketplace/ha-sedmitsa. Lite is complete on its own.

## Tests

```bash
python -m venv .venv && .venv/bin/pip install pytest-homeassistant-custom-component==0.13.371
make test PY=.venv/bin/python     # 122 tests against Home Assistant 2026.10
```

## Licence

MIT. Copyright (c) 2026 ПН СКРИПТС ЕООД (PN Scripts).
