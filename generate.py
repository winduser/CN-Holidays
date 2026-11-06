"""Generate cn-holidays.ics from the statutory holiday rules of the PRC.

The rules come from the National Holidays Regulations as amended by State
Council Decree No. 795 (effective 2025-01-01):
https://www.gov.cn/zhengce/content/202411/content_6986380.htm

Article 2 sets the holidays. Article 6 requires every holiday day that falls on a
Saturday or Sunday to be made up on a working day (补假); the regulations do not
say which one, so this script uses the first working days after the holiday,
following State Council practice. The yearly State Council notices that move
working days (调休) and add make-up working days (补班) are deliberately ignored,
so the calendar can be computed for any year without waiting for them.
"""

import datetime
import pathlib

from lunar_python import Lunar, Solar

# The amended regulations took effect on 2025-01-01, so FIRST_YEAR must not be earlier.
FIRST_YEAR = 2027
LAST_YEAR = 2027
OUTPUT = pathlib.Path(__file__).with_name("cn-holidays.ics")

SOURCE_URL = "https://www.gov.cn/zhengce/content/202411/content_6986380.htm"
LEGAL_BASIS = "依据《国务院关于修改〈全国年节及纪念日放假办法〉的决定》（国务院令第795号）。"
SCOPE_NOTE = "本日历列出法定假日及其周末补假，不含调休和补班安排。"
# A fixed DTSTAMP keeps regenerated output byte-identical when nothing changed.
DTSTAMP = "20241112T000000Z"


def lunar_to_solar(year, month, day):
    solar = Lunar.fromYmd(year, month, day).getSolar()
    return datetime.date(solar.getYear(), solar.getMonth(), solar.getDay())


def qingming(year):
    # The lunar year containing mid-April always holds that Gregorian year's Qingming.
    solar = Solar.fromYmd(year, 4, 15).getLunar().getJieQiTable()["清明"]
    date = datetime.date(solar.getYear(), solar.getMonth(), solar.getDay())
    if date.year != year or date.month != 4:
        raise ValueError(f"Unexpected Qingming date {date} for {year}")
    return date


def holidays(year):
    """Yield (slug, summary, first day, number of days, rule) for one year."""
    spring_festival = lunar_to_solar(year, 1, 1)
    yield "new-years-day", "元旦", datetime.date(year, 1, 1), 1, "放假1天（1月1日）"
    yield (
        "spring-festival",
        "春节",
        spring_festival - datetime.timedelta(days=1),
        4,
        "放假4天（农历除夕、正月初一至初三）",
    )
    yield "qingming", "清明节", qingming(year), 1, "放假1天（农历清明当日）"
    yield "labour-day", "劳动节", datetime.date(year, 5, 1), 2, "放假2天（5月1日、2日）"
    yield "dragon-boat", "端午节", lunar_to_solar(year, 5, 5), 1, "放假1天（农历端午当日）"
    yield "mid-autumn", "中秋节", lunar_to_solar(year, 8, 15), 1, "放假1天（农历中秋当日）"
    yield "national-day", "国庆节", datetime.date(year, 10, 1), 3, "放假3天（10月1日、2日、3日）"


def consecutive_runs(days):
    runs = []
    for day in days:
        if runs and day - runs[-1][-1] == datetime.timedelta(days=1):
            runs[-1].append(day)
        else:
            runs.append([day])
    return runs


def events(year):
    """Yield (UID stem, summary, first day, day after the last, description) for one year."""
    one_day = datetime.timedelta(days=1)
    statutory = sorted(holidays(year), key=lambda holiday: holiday[2])
    days_off = {
        first_day + offset * one_day
        for _, _, first_day, length, _ in statutory
        for offset in range(length)
    }
    for slug, summary, first_day, length, rule in statutory:
        end = first_day + length * one_day
        yield f"{year}-{slug}", summary, first_day, end, f"法定节假日，全体公民{rule}。{LEGAL_BASIS}{SCOPE_NOTE}"

        weekend_days = sum((first_day + offset * one_day).weekday() >= 5 for offset in range(length))
        make_up_days, candidate = [], end - one_day
        while len(make_up_days) < weekend_days:
            candidate += one_day
            if candidate.weekday() < 5 and candidate not in days_off:
                make_up_days.append(candidate)
                days_off.add(candidate)
        for index, run in enumerate(consecutive_runs(make_up_days), start=1):
            uid_stem = f"{year}-{slug}-make-up" + (f"-{index}" if index > 1 else "")
            description = (
                f"{summary}假日有{weekend_days}天适逢周六、周日，依《全国年节及纪念日放假办法》第六条在工作日补假。"
                f"{LEGAL_BASIS}{SCOPE_NOTE}"
            )
            yield uid_stem, f"{summary}补假", run[0], run[-1] + one_day, description


def escape(text):
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    """Fold a content line at 75 octets without splitting a UTF-8 character (RFC 5545 §3.1)."""
    pieces, current, limit = [], b"", 75
    for char in line:
        encoded = char.encode("utf-8")
        if len(current) + len(encoded) > limit:
            pieces.append(current)
            current, limit = b"", 74  # Continuation lines start with one space.
        current += encoded
    pieces.append(current)
    return "\r\n ".join(piece.decode("utf-8") for piece in pieces)


def build_calendar():
    years = str(FIRST_YEAR) if FIRST_YEAR == LAST_YEAR else f"{FIRST_YEAR}—{LAST_YEAR}"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CN-Holidays//Statutory Holidays of China//ZH",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:中国法定节假日",
        f"X-WR-CALDESC:{escape(f'全体公民放假的法定节假日（{years}年）。{LEGAL_BASIS}{SCOPE_NOTE}')}",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "REFRESH-INTERVAL;VALUE=DURATION:P1W",
        "X-PUBLISHED-TTL:P1W",
    ]
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        for uid_stem, summary, first_day, end, description in events(year):
            lines += [
                "BEGIN:VEVENT",
                f"UID:{uid_stem}@cn-holidays",
                f"DTSTAMP:{DTSTAMP}",
                f"DTSTART;VALUE=DATE:{first_day:%Y%m%d}",
                f"DTEND;VALUE=DATE:{end:%Y%m%d}",
                f"SUMMARY:{escape(summary)}",
                f"DESCRIPTION:{escape(description)}",
                f"URL:{SOURCE_URL}",
                "TRANSP:TRANSPARENT",
                "END:VEVENT",
            ]
    lines.append("END:VCALENDAR")
    return "".join(fold(line) + "\r\n" for line in lines)


if __name__ == "__main__":
    OUTPUT.write_bytes(build_calendar().encode("utf-8"))
    print(f"Wrote {OUTPUT}")
