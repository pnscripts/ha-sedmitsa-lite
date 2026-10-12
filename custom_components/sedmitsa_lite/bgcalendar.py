"""Bulgarian working-day calendar: official holidays, moved days off and declared
non-working days.

Pure Python, no Home Assistant imports, so it can be tested and reused alone.

Sources (checked by PN Scripts):
- Labour Code (Кодекс на труда), art. 154: the official holidays, and par. 2:
  when a holiday other than Easter falls on a Saturday or Sunday, the first
  working day (or two) after it is a day off.
- Council of Ministers decision of 19 November 2025: 31 December 2025 and
  2 January 2026 are non-working days (euro changeover).

Sedmitsa Lite by PN Scripts. Copyright (c) 2026 ПН СКРИПТС ЕООД / PN Scripts. MIT licence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import StrEnum
from typing import Iterable, Iterator, Mapping

MIN_YEAR = 2013
MAX_YEAR = 2099
WORK_HOURS_PER_DAY = 8


class DayKind(StrEnum):
    """What kind of day a date is."""

    WORKING_DAY = "working_day"
    WEEKEND = "weekend"
    PUBLIC_HOLIDAY = "public_holiday"
    MOVED_DAY_OFF = "moved_day_off"
    DECLARED_DAY_OFF = "declared_day_off"
    CUSTOM_DAY_OFF = "custom_day_off"
    CUSTOM_WORKING_DAY = "custom_working_day"


DAYS_OFF = frozenset(
    {
        DayKind.WEEKEND,
        DayKind.PUBLIC_HOLIDAY,
        DayKind.MOVED_DAY_OFF,
        DayKind.DECLARED_DAY_OFF,
        DayKind.CUSTOM_DAY_OFF,
    }
)


@dataclass(frozen=True, slots=True)
class Name:
    """A name in English and Bulgarian."""

    en: str
    bg: str

    def get(self, language: str) -> str:
        return self.bg if language == "bg" else self.en


@dataclass(frozen=True, slots=True)
class Day:
    """One classified date."""

    date: date
    kind: DayKind
    names: tuple[Name, ...] = ()

    @property
    def is_working(self) -> bool:
        return self.kind not in DAYS_OFF

    def name(self, language: str = "en") -> str:
        return "; ".join(n.get(language) for n in self.names)


# Fixed-date official holidays, Labour Code art. 154(1).
FIXED_HOLIDAYS: dict[tuple[int, int], Name] = {
    (1, 1): Name("New Year's Day", "Нова година"),
    (3, 3): Name("Liberation Day", "Ден на Освобождението на България"),
    (5, 1): Name("Labour Day", "Ден на труда"),
    (5, 6): Name(
        "St George's Day, Day of Bravery and the Bulgarian Army",
        "Гергьовден, Ден на храбростта и Българската армия",
    ),
    (5, 24): Name(
        "Day of the Bulgarian Alphabet, Education and Culture",
        "Ден на българската азбука, просвета и култура",
    ),
    (9, 6): Name("Unification Day", "Ден на Съединението"),
    (9, 22): Name("Independence Day", "Ден на Независимостта"),
    (12, 24): Name("Christmas Eve", "Бъдни вечер"),
    (12, 25): Name("Christmas Day", "Рождество Христово"),
    (12, 26): Name("Christmas, second day", "Рождество Христово, втори ден"),
}

EASTER_NAMES = {
    -2: Name("Good Friday", "Разпети петък"),
    -1: Name("Holy Saturday", "Велика събота"),
    0: Name("Easter Sunday", "Великден"),
    1: Name("Easter Monday", "Великден, втори ден"),
}

ENLIGHTENERS_DAY = Name(
    "Day of the Bulgarian Enlighteners (day off for schools and universities)",
    "Ден на народните будители (неучебен ден)",
)


def _moved_name(holiday: Name, holiday_date: date) -> Name:
    return Name(
        f"Day off for {holiday.en} ({holiday_date:%d.%m})",
        f"Почивен ден за {holiday.bg} ({holiday_date:%d.%m})",
    )


# Non-working days declared by the Council of Ministers.
DECLARED_DAYS_OFF: dict[date, Name] = {
    date(2025, 12, 31): Name(
        "Non-working day declared by the government (euro changeover)",
        "Неприсъствен ден по решение на Министерския съвет (въвеждане на еврото)",
    ),
    date(2026, 1, 2): Name(
        "Non-working day declared by the government (euro changeover)",
        "Неприсъствен ден по решение на Министерския съвет (въвеждане на еврото)",
    ),
}


def orthodox_easter(year: int) -> date:
    """Orthodox Easter Sunday as a Gregorian date (Meeus' Julian algorithm)."""
    if not 1900 <= year <= 2099:
        raise ValueError(f"year {year} is outside 1900-2099")
    a, b, c = year % 4, year % 7, year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month, day = divmod(d + e + 114, 31)
    # Julian to Gregorian: 13 days in 1900-2099.
    return date(year, month, day + 1) + timedelta(days=13)


@dataclass(slots=True)
class Settings:
    """User choices that change the calendar."""

    workdays: frozenset[int] = frozenset({0, 1, 2, 3, 4})  # Monday = 0
    enlighteners_day_off: bool = False
    use_declared_days: bool = True
    custom_days_off: dict[date, str] = field(default_factory=dict)
    custom_working_days: dict[date, str] = field(default_factory=dict)
    hours_per_day: float = WORK_HOURS_PER_DAY


class BulgarianCalendar:
    """Classifies dates for Bulgaria; caches each year."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._years: dict[int, dict[date, Day]] = {}

    # ----- holidays -----------------------------------------------------

    @staticmethod
    def official_holidays(year: int) -> dict[date, Name]:
        """Official holidays of art. 154(1), by date (Easter may share a date)."""
        _check_year(year)
        found: dict[date, list[Name]] = {}
        for (month, day), name in FIXED_HOLIDAYS.items():
            found.setdefault(date(year, month, day), []).append(name)
        easter = orthodox_easter(year)
        for offset, name in EASTER_NAMES.items():
            found.setdefault(easter + timedelta(days=offset), []).append(name)
        return {d: _join(names) for d, names in sorted(found.items())}

    def _build_year(self, year: int) -> dict[date, Day]:
        s = self.settings
        holidays = self.official_holidays(year)
        days: dict[date, Day] = {d: Day(d, DayKind.PUBLIC_HOLIDAY, (n,)) for d, n in holidays.items()}

        if s.enlighteners_day_off:
            nov1 = date(year, 11, 1)
            if nov1 not in days:
                days[nov1] = Day(nov1, DayKind.PUBLIC_HOLIDAY, (ENLIGHTENERS_DAY,))

        for target, holiday, held_on in self._moved_days(year):
            if target.year == year:
                days[target] = Day(target, DayKind.MOVED_DAY_OFF, (_moved_name(holiday, held_on),))

        if s.use_declared_days:
            for d, name in DECLARED_DAYS_OFF.items():
                if d.year == year and d not in days:
                    days[d] = Day(d, DayKind.DECLARED_DAY_OFF, (name,))

        for d, label in s.custom_days_off.items():
            if d.year == year and (d not in days or days[d].is_working):
                days[d] = Day(d, DayKind.CUSTOM_DAY_OFF, (Name(label or "Day off", label or "Почивен ден"),))
        for d, label in s.custom_working_days.items():
            if d.year == year:
                days[d] = Day(d, DayKind.CUSTOM_WORKING_DAY, (Name(label or "Working day", label or "Работен ден"),))
        return days

    def _moved_days(self, year: int) -> list[tuple[date, Name, date]]:
        """Days off of art. 154(2) that land in `year` (from this or last year).

        A fixed-date holiday on a Saturday or Sunday gives a day off on the
        first working day after it that is not itself a holiday or already
        given; Easter days never move. A fixed holiday that shares its date
        with an Easter day (1 May on Holy Saturday in 2021) still moves.
        """
        blocked: set[date] = set()
        sources = [y for y in (year - 1, year) if y >= MIN_YEAR]
        for y in sources:
            blocked |= set(self.official_holidays(y))
        blocked |= set(self.official_holidays(year + 1)) if year < MAX_YEAR else set()
        if self.settings.use_declared_days:
            blocked |= set(DECLARED_DAYS_OFF)
        out: list[tuple[date, Name, date]] = []
        taken: set[date] = set()
        for y in sources:
            for (month, day), name in sorted(FIXED_HOLIDAYS.items()):
                held_on = date(y, month, day)
                if held_on.weekday() < 5:
                    continue
                target = held_on + timedelta(days=1)
                while target.weekday() >= 5 or target in blocked or target in taken:
                    target += timedelta(days=1)
                taken.add(target)
                out.append((target, name, held_on))
        return out

    @staticmethod
    def _declared() -> dict[date, Name]:
        return DECLARED_DAYS_OFF

    def _year(self, year: int) -> dict[date, Day]:
        _check_year(year)
        if year not in self._years:
            self._years[year] = self._build_year(year)
        return self._years[year]

    # ----- queries ------------------------------------------------------

    def day(self, d: date) -> Day:
        """Classify one date."""
        special = self._year(d.year).get(d)
        if special is not None:
            return special
        if d.weekday() in self.settings.workdays:
            return Day(d, DayKind.WORKING_DAY)
        return Day(d, DayKind.WEEKEND)

    def is_working_day(self, d: date) -> bool:
        return self.day(d).is_working

    def special_days(self, start: date, end: date) -> list[Day]:
        """Holidays and changed days in [start, end], in date order."""
        out: list[Day] = []
        for year in range(start.year, end.year + 1):
            for d, day in sorted(self._year(year).items()):
                if start <= d <= end:
                    out.append(day)
        return out

    def working_days(self, start: date, end: date) -> int:
        """Working days in [start, end], both included."""
        if end < start:
            return 0
        return sum(1 for d in _dates(start, end) if self.is_working_day(d))

    def working_hours(self, start: date, end: date) -> float:
        return self.working_days(start, end) * self.settings.hours_per_day

    def month_working_days(self, year: int, month: int) -> int:
        first = date(year, month, 1)
        return self.working_days(first, _month_end(first))

    def add_working_days(self, start: date, count: int) -> date:
        """The date `count` working days after `start` (before it if negative).

        `start` itself is not counted, like a deadline "in 14 working days".
        """
        step = 1 if count >= 0 else -1
        remaining = abs(count)
        d = start
        while remaining:
            d += timedelta(days=step)
            if self.is_working_day(d):
                remaining -= 1
        return d

    def next_working_day(self, after: date) -> date:
        return self.add_working_days(after, 1)

    def next_day_off(self, on_or_after: date, include_weekends: bool = False) -> Day:
        """The next non-working day; by default skips ordinary weekends."""
        d = on_or_after
        for _ in range(800):
            day = self.day(d)
            if not day.is_working and (include_weekends or day.kind != DayKind.WEEKEND):
                return day
            d += timedelta(days=1)
        raise LookupError("no day off within 800 days")


# ----- helpers ------------------------------------------------------------


def _check_year(year: int) -> None:
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise ValueError(f"Sedmitsa covers {MIN_YEAR} to {MAX_YEAR}, not {year}")


def _join(names: list[Name]) -> Name:
    return Name("; ".join(n.en for n in names), "; ".join(n.bg for n in names))




def _dates(start: date, end: date) -> Iterator[date]:
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def _month_end(first: date) -> date:
    nxt = date(first.year + (first.month == 12), first.month % 12 + 1, 1)
    return nxt - timedelta(days=1)


def parse_date_list(text: str) -> dict[date, str]:
    """Parse lines "2026-12-31 Office closed" (label optional; ; or , separated)."""
    out: dict[date, str] = {}
    for raw in text.replace(";", "\n").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        token, _, label = line.partition(" ")
        token = token.rstrip(",")
        try:
            if "." in token:
                dd, mm, yy = token.split(".")
                d = date(int(yy), int(mm), int(dd))
            else:
                d = date.fromisoformat(token)
        except ValueError as err:
            raise ValueError(f"not a date: {token!r}") from err
        out[d] = label.strip()
    return out
