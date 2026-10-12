"""The calendar rules, checked against published Bulgarian calendars."""

from datetime import date

import pytest

from custom_components.sedmitsa_lite.bgcalendar import (
    BulgarianCalendar,
    DayKind,
    Settings,
    orthodox_easter,
    parse_date_list,
)

D = date


@pytest.mark.parametrize(
    ("year", "easter"),
    [
        (2013, D(2013, 5, 5)),
        (2020, D(2020, 4, 19)),
        (2021, D(2021, 5, 2)),
        (2022, D(2022, 4, 24)),
        (2023, D(2023, 4, 16)),
        (2024, D(2024, 5, 5)),
        (2025, D(2025, 4, 20)),
        (2026, D(2026, 4, 12)),
        (2027, D(2027, 5, 2)),
        (2028, D(2028, 4, 16)),
        (2030, D(2030, 4, 28)),
    ],
)
def test_orthodox_easter(year, easter):
    assert orthodox_easter(year) == easter
    assert easter.weekday() == 6


def days_off(year, **kw):
    cal = BulgarianCalendar(Settings(**kw))
    return {
        d.date: d.kind
        for d in cal.special_days(D(year, 1, 1), D(year, 12, 31))
        if d.kind != DayKind.PUBLIC_HOLIDAY
    }


def test_2026_matches_the_published_calendar():
    # Published calendar for 2026: 25.05, 07.09 and 28.12 are moved days off,
    # 02.01 is a non-working day by government decision.
    assert days_off(2026) == {
        D(2026, 1, 2): DayKind.DECLARED_DAY_OFF,
        D(2026, 5, 25): DayKind.MOVED_DAY_OFF,
        D(2026, 9, 7): DayKind.MOVED_DAY_OFF,
        D(2026, 12, 28): DayKind.MOVED_DAY_OFF,
    }
    cal = BulgarianCalendar()
    assert cal.working_days(D(2026, 1, 1), D(2026, 12, 31)) == 248
    assert BulgarianCalendar(Settings(use_declared_days=False)).working_days(D(2026, 1, 1), D(2026, 12, 31)) == 249


def test_2025():
    assert days_off(2025) == {
        D(2025, 5, 26): DayKind.MOVED_DAY_OFF,
        D(2025, 9, 8): DayKind.MOVED_DAY_OFF,
        D(2025, 12, 31): DayKind.DECLARED_DAY_OFF,
    }


def test_christmas_on_a_weekend_moves_two_days():
    # 2022: 24 Sat, 25 Sun, 26 Mon -> 27 and 28 December off.
    assert days_off(2022) == {
        D(2022, 1, 3): DayKind.MOVED_DAY_OFF,  # 1 January on a Saturday
        D(2022, 5, 2): DayKind.MOVED_DAY_OFF,  # 1 May on a Sunday
        D(2022, 12, 27): DayKind.MOVED_DAY_OFF,
        D(2022, 12, 28): DayKind.MOVED_DAY_OFF,
    }
    # 2021: 25 Sat, 26 Sun -> 27 and 28 December.
    assert D(2021, 12, 27) in days_off(2021) and D(2021, 12, 28) in days_off(2021)


def test_may_day_on_holy_saturday_moves_past_easter_monday():
    # 2021: 1 May was Holy Saturday; Easter Monday was 3 May, so 4 May is off.
    cal = BulgarianCalendar()
    assert cal.day(D(2021, 5, 1)).kind == DayKind.PUBLIC_HOLIDAY
    assert "Labour Day" in cal.day(D(2021, 5, 1)).name("en")
    assert "Holy Saturday" in cal.day(D(2021, 5, 1)).name("en")
    assert cal.day(D(2021, 5, 4)).kind == DayKind.MOVED_DAY_OFF
    assert cal.day(D(2021, 5, 5)).is_working
    # 2027 has the same shape.
    assert cal.day(D(2027, 5, 4)).kind == DayKind.MOVED_DAY_OFF


def test_easter_days_never_move():
    cal = BulgarianCalendar()
    # Easter Sunday 2026 is 12 April; Monday 13 is Easter Monday, 14 is a working day.
    assert cal.day(D(2026, 4, 12)).kind == DayKind.PUBLIC_HOLIDAY
    assert cal.day(D(2026, 4, 13)).kind == DayKind.PUBLIC_HOLIDAY
    assert cal.day(D(2026, 4, 14)).kind == DayKind.WORKING_DAY


def test_st_george_on_easter_monday_does_not_add_a_day():
    # 2024: 6 May was both St George's Day and Easter Monday; 7 May was a working day.
    cal = BulgarianCalendar()
    assert cal.day(D(2024, 5, 6)).kind == DayKind.PUBLIC_HOLIDAY
    assert cal.day(D(2024, 5, 7)).is_working


def test_bulgarian_names():
    cal = BulgarianCalendar()
    assert cal.day(D(2026, 3, 3)).name("bg") == "Ден на Освобождението на България"
    assert cal.day(D(2026, 12, 28)).name("bg") == "Почивен ден за Рождество Христово, втори ден (26.12)"
    assert cal.day(D(2026, 12, 28)).name("en") == "Day off for Christmas, second day (26.12)"


def test_enlighteners_day_is_optional():
    assert BulgarianCalendar().day(D(2027, 11, 1)).is_working
    cal = BulgarianCalendar(Settings(enlighteners_day_off=True))
    assert cal.day(D(2027, 11, 1)).kind == DayKind.PUBLIC_HOLIDAY
    # It is not an art. 154 holiday, so it never moves: 1 Nov 2026 is a Sunday.
    assert cal.day(D(2026, 11, 2)).is_working


def test_custom_days_and_working_saturday():
    cal = BulgarianCalendar(
        Settings(
            custom_days_off={D(2026, 12, 31): "Office closed"},
            custom_working_days={D(2026, 12, 19): "Inventory", D(2026, 5, 25): ""},
        )
    )
    assert cal.day(D(2026, 12, 31)).kind == DayKind.CUSTOM_DAY_OFF
    assert cal.day(D(2026, 12, 31)).name("en") == "Office closed"
    assert cal.day(D(2026, 12, 19)).kind == DayKind.CUSTOM_WORKING_DAY
    assert cal.day(D(2026, 5, 25)).is_working
    assert cal.day(D(2026, 5, 25)).name("bg") == "Работен ден"
    # A custom day off on a holiday keeps the holiday.
    cal2 = BulgarianCalendar(Settings(custom_days_off={D(2026, 3, 3): "x"}))
    assert cal2.day(D(2026, 3, 3)).kind == DayKind.PUBLIC_HOLIDAY


def test_six_day_week():
    cal = BulgarianCalendar(Settings(workdays=frozenset(range(6))))
    assert cal.day(D(2026, 10, 10)).is_working  # Saturday
    assert not cal.day(D(2026, 10, 11)).is_working
    assert cal.month_working_days(2026, 10) == 27


def test_month_counts_and_hours():
    cal = BulgarianCalendar()
    assert [cal.month_working_days(2026, m) for m in range(1, 13)] == [20, 20, 21, 20, 18, 22, 23, 21, 20, 22, 21, 20]
    assert cal.working_hours(D(2026, 12, 1), D(2026, 12, 31)) == 160
    assert BulgarianCalendar(Settings(hours_per_day=7)).working_hours(D(2026, 12, 1), D(2026, 12, 31)) == 140
    assert cal.working_days(D(2026, 12, 31), D(2026, 12, 1)) == 0


def test_add_working_days():
    cal = BulgarianCalendar()
    # 14 working days after Friday 18 Dec 2026 skips Christmas and New Year.
    assert cal.add_working_days(D(2026, 12, 18), 14) == D(2027, 1, 13)
    assert cal.add_working_days(D(2026, 12, 23), 1) == D(2026, 12, 29)
    assert cal.add_working_days(D(2026, 12, 29), -1) == D(2026, 12, 23)
    assert cal.add_working_days(D(2026, 5, 1), 0) == D(2026, 5, 1)
    assert cal.next_working_day(D(2026, 12, 23)) == D(2026, 12, 29)


def test_next_day_off():
    cal = BulgarianCalendar()
    nxt = cal.next_day_off(D(2026, 10, 11))
    assert nxt.date == D(2026, 12, 24)
    assert cal.next_day_off(D(2026, 10, 9), include_weekends=True).date == D(2026, 10, 10)


def test_year_boundaries():
    cal = BulgarianCalendar()
    with pytest.raises(ValueError):
        cal.day(D(2012, 6, 1))
    with pytest.raises(ValueError):
        cal.day(D(2100, 1, 4))
    assert cal.day(D(2099, 12, 25)).kind == DayKind.PUBLIC_HOLIDAY


@pytest.mark.parametrize("year", range(2013, 2100))
def test_every_year_is_consistent(year):
    cal = BulgarianCalendar(Settings(use_declared_days=False))
    special = cal.special_days(D(year, 1, 1), D(year, 12, 31))
    holidays = [d for d in special if d.kind == DayKind.PUBLIC_HOLIDAY]
    moved = [d for d in special if d.kind == DayKind.MOVED_DAY_OFF]
    assert 12 <= len(holidays) <= 14
    # Every fixed holiday on a weekend gives exactly one moved day off on a weekday.
    fixed_on_weekend = sum(
        1 for (m, dd) in [(1, 1), (3, 3), (5, 1), (5, 6), (5, 24), (9, 6), (9, 22), (12, 24), (12, 25), (12, 26)]
        if D(year, m, dd).weekday() >= 5
    )
    # Christmas moves land on 27 to 29 December, so nothing crosses into January.
    assert len(moved) == fixed_on_weekend
    assert all(d.date.weekday() < 5 for d in moved)
    assert len({d.date for d in special}) == len(special)


def test_parse_date_list():
    assert parse_date_list("2026-12-31 Office closed\n# comment\n\n02.01.2027") == {
        D(2026, 12, 31): "Office closed",
        D(2027, 1, 2): "",
    }
    assert parse_date_list("2026-12-31; 2027-01-04 Stocktake") == {D(2026, 12, 31): "", D(2027, 1, 4): "Stocktake"}
    with pytest.raises(ValueError):
        parse_date_list("31/12/2026")
    with pytest.raises(ValueError):
        parse_date_list("2026-02-30")


# ----- school ---------------------------------------------------------------


def school(group):
    return SchoolCalendar(BulgarianCalendar(), GradeGroup(group))
