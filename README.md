# CN-Holidays

`cn-holidays.ics` is a subscribable calendar of the public holidays of the People’s Republic of China for 2027; `FIRST_YEAR` and `LAST_YEAR` in `generate.py` set the range. It follows Article 2 of the National Holidays Regulations (《全国年节及纪念日放假办法》) as amended by [State Council Decree No. 795](https://www.gov.cn/zhengce/content/202411/content_6986380.htm), which took effect on 1 January 2025. It lists only the days the regulations grant to all citizens: New Year’s Day (1 day), the Spring Festival (4 days, from Lunar New Year’s Eve to the third day of the first lunar month), Qingming (1 day), Labour Day (2 days, 1–2 May), the Dragon Boat Festival (1 day), the Mid-Autumn Festival (1 day), and National Day (3 days, 1–3 October).

Article 6 requires each holiday day that falls on a Saturday or Sunday to be made up on a working day (补假). The regulations do not say which working day, so the calendar follows State Council practice and uses the first working days after the holiday that are not themselves holidays; these appear as separate events such as “春节补假”. In 2027, for example, two Spring Festival days fall on 6 and 7 February, so 9 and 10 February are added. The calendar deliberately omits the yearly State Council arrangements that shift days off (调休) and add make-up working days (补班), so the actual days off in a given year can still differ from this calendar. Partial holidays such as Women’s Day and Youth Day are left out, and Article 6 gives them no make-up days in any case. When two holidays share a weekday, as the Mid-Autumn Festival and National Day would on 1 October 2031, the regulations provide no make-up day and the calendar adds none.

## Subscribe

Add the calendar by URL in Fantastical, Apple Calendar, Google Calendar, Outlook, or any client that accepts iCalendar subscriptions.

```
https://raw.githubusercontent.com/winduser/CN-Holidays/main/cn-holidays.ics
```

Apple devices also accept the same address with the `webcal://` scheme, which opens the subscription dialog directly.

## Regenerate

The lunar dates and the Qingming solar term come from [lunar_python](https://github.com/6tail/lunar-python). To extend the range or change the rules, edit `generate.py` and run:

```
python3 -m pip install -r requirements.txt
python3 generate.py
```

The generated dates for 2025–2050 were checked against two independent sources: the `lunardate` package for lunar dates, and an astronomical computation of the Sun reaching 15° ecliptic longitude in Beijing time (Skyfield with the JPL DE440s ephemeris) for Qingming. All 182 events in that range matched.
