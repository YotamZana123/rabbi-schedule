import streamlit as st
import pandas as pd
from calendar_manager import get_shabbats_for_year
import db_manager
import datetime
from pyluach import hebrewcal

st.set_page_config(page_title="סבב רב", layout="wide")

# RTL CSS Injection & Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;700&display=swap');

    body, .stApp {
        direction: rtl;
        font-family: 'Frank Ruhl Libre', serif;
        background-color: #faf9f6; /* צבע רקע קרם עדין - דמוי קלף */
    }
    .stSelectbox label, div[data-testid="stDataFrame"] {
        direction: rtl;
        font-family: 'Frank Ruhl Libre', serif;
    }
    /* מרכוז כל הכותרות והטקסטים ושינוי צבעים */
    h1, h2, h3, h4, p, .stMarkdown {
        text-align: center !important;
        font-family: 'Frank Ruhl Libre', serif;
    }
    h1 {
        color: #0f2557 !important; /* כחול עמוק */
        text-shadow: 1px 1px 2px rgba(212, 175, 55, 0.3); /* צל זהב עדין */
        padding-bottom: 10px;
        border-bottom: 2px solid #d4af37; /* קו זהב תחתון */
        margin-bottom: 20px;
    }
    h3 {
        color: #1a3673 !important;
    }
    /* עיצוב כפתורים בסגנון תורני/מזמין */
    .stButton > button {
        background-color: #0f2557 !important;
        color: #ffffff !important;
        border: 1px solid #d4af37 !important;
        border-radius: 8px !important;
        font-family: 'Frank Ruhl Libre', serif;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #d4af37 !important;
        color: #0f2557 !important;
        border: 1px solid #0f2557 !important;
    }
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("סבב הרב משה ביגל שליט״א")

db_manager.init_db()

# Year selector
def format_year(y):
    return f"{hebrewcal.Year(y).year_string()} ({y})"

# מרכוז שדה הבחירה
col_space1, col_center, col_space3 = st.columns([1, 2, 1])
with col_center:
    selected_year = st.selectbox("בחר שנת לוח:", range(5785, 5800), index=2, format_func=format_year)

shabbats = get_shabbats_for_year(selected_year)

year_str_hebrew = shabbats[0]['year_str'] if shabbats else ""
st.subheader(f"לוח שבתות וחגים לשנת {year_str_hebrew}")

# We will build a list of dictionaries for the dataframe
data = []
for i, sh in enumerate(shabbats):
    date_str = sh['hebrew_date_str']
    greg_str = sh['gregorian_date'].strftime("%d-%m-%Y")
    
    event = sh['parsha']
    if not event and sh['holiday']:
        event = sh['holiday']
    elif sh['holiday']:
        event += f" ({sh['holiday']})"
        
    notes = "שבת מברכין" if sh['is_mevarchim'] else ""
    
    # שבת הגדול - השבת שלפני פסח (חלה תמיד בניסן בין ה-8 ל-14 לחודש)
    # חודש ניסן הוא חודש 1 בספריית pyluach
    if sh['date'].month == 1 and 8 <= sh['date'].day <= 14:
        if notes:
            notes += " | דרשת שבת הגדול"
        else:
            notes = "דרשת שבת הגדול"
            
    # מציאת המיקום של השבת הנוכחית בתוך החודש העברי
    month_shabbats_before = 0
    is_saturday = (sh['date'].weekday() == 7)
    
    if is_saturday:
        for j in range(i - 1, -1, -1):
            if shabbats[j]['date'].weekday() == 7:
                if shabbats[j]['date'].month == sh['date'].month:
                    month_shabbats_before += 1
                else:
                    break
    
    # Check DB for assignment
    assignment = db_manager.get_assignment(sh['date'].year, sh['date'].month, sh['date'].day)
    
    if assignment:
        fn = assignment['friday_night']
        sm = assignment['shabbat_morning']
        ss = assignment['seuda_shlishit']
    else:
        # Default Logic
        if "כי תבא" in event or "כי תבוא" in event or "נצבים" in event or "וילך" in event:
            fn, sm, ss = "", "", ""
        elif "כיפור" in event:
            fn, sm, ss = "מרכזי", "מרכזי", "/"
        elif sh['is_mevarchim']:
            fn, sm, ss = "חב״ד", "מרכזי", "כלניות"
        elif is_saturday:
            if month_shabbats_before == 0:
                fn, sm, ss = "רבין/מרגלית", "אור שלום", "אהבת ישראל"
            elif month_shabbats_before == 1:
                fn, sm, ss = "צפוני", "אשכנז", "נעימת חיים"
            elif month_shabbats_before == 2:
                fn, sm, ss = "דרכי נועם", "אהבת ישראל", "דרכי נועם"
            elif month_shabbats_before == 3:
                fn, sm, ss = "נעימת חיים", "הרשטוק", "צפוני"
            else:
                fn, sm, ss = "נעימת חיים", "תימני", "צפוני"
        else:
            fn, sm, ss = "", "", ""
            
        # חסימת סעודה שלישית בחגים ספציפיים
        if "ראש השנה" in event or "עצרת" in event or "שמחת תורה" in event or "פסח" in event or "שבועות" in event:
            ss = "/"
            
    data.append({
        "Year": sh['date'].year,
        "Month": sh['date'].month,
        "Day": sh['date'].day,
        "Month_Name": sh['month_name'],
        "פרשה/מועד": event,
        "תאריך עברי": date_str,
        "תאריך לועזי": greg_str,
        "כניסת שבת/חג": sh['candles'],
        "צאת שבת/חג": sh['havdalah'],
        "ליל שבת": fn,
        "שבת שחרית": sm,
        "סעודה שלישית": ss,
        "הערות": notes
    })

df = pd.DataFrame(data)

def generate_html_table(df):
    html = """
<style>
.schedule-table { width: 100%; border-collapse: collapse; direction: rtl; font-family: 'Frank Ruhl Libre', sans-serif; }
.schedule-table th, .schedule-table td { border: 1px solid #ddd; padding: 8px; text-align: center; }
.schedule-table th { background-color: #002B5B; color: #D4AF37; }

/* עיצוב רספונסיבי למובייל - הופך את השורות לכרטיסיות */
@media screen and (max-width: 768px) {
    .schedule-table thead { display: none; }
    .schedule-table, .schedule-table tbody, .schedule-table tr, .schedule-table td { display: block; width: 100%; box-sizing: border-box; }
    .schedule-table tr { margin-bottom: 20px; border: 2px solid #002B5B; border-radius: 8px; background-color: #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .schedule-table td { border: none; border-bottom: 1px solid #eee; position: relative; padding-right: 45%; text-align: left !important; min-height: 35px; }
    .schedule-table td:before { 
        content: attr(data-label); 
        position: absolute; right: 10px; width: 40%; 
        white-space: nowrap; font-weight: bold; text-align: right; color: #002B5B;
    }
    .schedule-table td:last-child { border-bottom: none; }
}
</style>
<table class="schedule-table">
<thead>
    <tr>
        <th>פרשה/מועד</th>
        <th>תאריך עברי</th>
        <th>תאריך לועזי</th>
        <th>כניסה</th>
        <th>יציאה</th>
        <th>ליל שבת</th>
        <th>שחרית</th>
        <th>סעודה 3</th>
        <th>הערות</th>
    </tr>
</thead>
<tbody>
"""
    for _, row in df.iterrows():
        ss_val = row["סעודה שלישית"]
        ss_style = f' style="background-color: #e8e8e8; color: #a0a0a0; font-weight: bold;"' if ss_val == "/" else ""
        html += f"""<tr>
<td data-label="פרשה/מועד"><b>{row['פרשה/מועד']}</b></td>
<td data-label="תאריך עברי">{row['תאריך עברי']}</td>
<td data-label="תאריך לועזי" dir="ltr">{row['תאריך לועזי']}</td>
<td data-label="כניסה">{row['כניסת שבת/חג']}</td>
<td data-label="יציאה">{row['צאת שבת/חג']}</td>
<td data-label="ליל שבת">{row['ליל שבת']}</td>
<td data-label="שחרית">{row['שבת שחרית']}</td>
<td data-label="סעודה 3"{ss_style}>{ss_val}</td>
<td data-label="הערות">{row['הערות']}</td>
</tr>
"""
    html += "</tbody></table>"
    return html

# יצירת כרטיסיות לפי חודשים
unique_months = df['Month_Name'].unique()
tabs = st.tabs(list(unique_months))

for i, tab in enumerate(tabs):
    with tab:
        month_df = df[df['Month_Name'] == unique_months[i]]
        st.html(generate_html_table(month_df))

# העברת הכפתורים לסיידבר
st.sidebar.markdown("### פעולות")

@st.dialog("✏️ עריכת שיבוץ")
def edit_dialog():
    selected_event = st.selectbox("בחר שבת לעריכה:", df["פרשה/מועד"].tolist())
    if selected_event:
        row = df[df["פרשה/מועד"] == selected_event].iloc[0]
        st.write(f"**שיבוץ נוכחי ל{selected_event}:**")
        new_fn = st.text_input("ליל שבת", value=row["ליל שבת"])
        new_sm = st.text_input("שבת שחרית", value=row["שבת שחרית"])
        new_ss = st.text_input("סעודה שלישית", value=row["סעודה שלישית"])
        
        if st.button("שמור שינויים", type="primary"):
            db_manager.save_assignment(
                int(row["Year"]), int(row["Month"]), int(row["Day"]),
                selected_event, new_fn, new_sm, new_ss
            )
            st.success("נשמר בהצלחה!")
            st.rerun()

if st.sidebar.button("✏️ עריכת שיבוץ", use_container_width=True):
    edit_dialog()

if st.sidebar.button("⬇️ הורדת PDF (בקרוב)", use_container_width=True):
    st.sidebar.info("כפתור זה יאפשר הורדה של הלוח להדפסה.")

if st.sidebar.button("💬 שליחה בוואטסאפ (בקרוב)", use_container_width=True):
    st.sidebar.info("כפתור זה יאפשר שליחה מהירה של הלוח בוואטסאפ.")
