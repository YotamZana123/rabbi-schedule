import requests
from pyluach import dates, parshios, hebrewcal
import datetime

def get_shabbats_for_year(hebrew_year):
    shabbats = []
    year = hebrewcal.Year(hebrew_year)
    
    # חישוב תאריכים לועזיים לתחילת וסוף השנה העברית כדי למשוך זמנים מה-API
    start_greg = dates.HebrewDate(hebrew_year, 7, 1).to_pydate().isoformat() # Tishrei is month 7 in pyluach
    end_greg = dates.HebrewDate(hebrew_year, 6, 29).to_pydate().isoformat() # Elul is month 6

    
    # קריאה ל-Hebcal עבור מיתר (קואורדינטות של מיתר)
    url = f'https://www.hebcal.com/hebcal?v=1&cfg=json&c=on&geo=pos&latitude=31.3283&longitude=34.9387&tzid=Asia/Jerusalem&start={start_greg}&end={end_greg}'
    try:
        res = requests.get(url).json()
        items = res.get('items', [])
    except:
        items = []

    candle_times = {}
    havdalah_times = {}
    
    for item in items:
        if item['category'] == 'candles':
            d = item['date'][:10]
            t = item['date'][11:16]
            candle_times[d] = t
        elif item['category'] == 'havdalah':
            d = item['date'][:10]
            t = item['date'][11:16]
            havdalah_times[d] = t

    for day in year.iterdates():
        holiday = day.holiday(israel=True, hebrew=True)
        is_saturday = (day.weekday() == 7)
        
        # נשמור רק שבתות, וימים טובים מרכזיים (כדי לסנן את חול המועד וימי חול)
        m, d = day.month, day.day
        is_yom_tov = False
        if m == 7 and d in [1, 2, 10, 15, 22]: is_yom_tov = True # ר"ה, כיפור, סוכות א, שמיני עצרת
        if m == 1 and d in [15, 21]: is_yom_tov = True # פסח א, פסח ז
        if m == 3 and d == 6: is_yom_tov = True # שבועות
        
        if is_saturday or is_yom_tov:
            parsha_idx = parshios.getparsha(day, israel=True)
            parsha_name = ""
            
            if parsha_idx is not None:
                if isinstance(parsha_idx, list):
                    parsha_name = " - ".join([parshios.PARSHIOS_HEBREW[i] for i in parsha_idx])
                else:
                    parsha_name = parshios.PARSHIOS_HEBREW[parsha_idx]
            
            if not parsha_name and holiday:
                parsha_name = holiday
            elif parsha_name and holiday:
                parsha_name = f"{parsha_name} ({holiday})"

            is_mevarchim = False
            if day.month != 6 and is_saturday: # שבת מברכין זה רק בשבת
                try:
                    next_shabbat = day + 7
                    if next_shabbat.month != day.month:
                        is_mevarchim = True
                except ValueError:
                    is_mevarchim = True

            hebrew_date_str = day.hebrew_date_string().rsplit(' ', 1)[0]
            year_str = year.year_string()
            
            curr_greg = day.to_pydate().isoformat()
            prev_greg = (day - 1).to_pydate().isoformat()
            
            shabbats.append({
                "date": day,
                "gregorian_date": day.to_pydate(),
                "parsha": parsha_name,
                "is_mevarchim": is_mevarchim,
                "holiday": holiday,
                "hebrew_date_str": hebrew_date_str,
                "year_str": year_str,
                "candles": candle_times.get(prev_greg, ""),
                "havdalah": havdalah_times.get(curr_greg, ""),
                "month_name": day.month_name(hebrew=True)
            })
            
    return shabbats
