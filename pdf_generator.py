import os
import pandas as pd
from fpdf import FPDF
from fpdf.fonts import FontFace
from bidi.algorithm import get_display

def bidi_text(text):
    if not text: return ""
    return "\n".join(get_display(line) for line in text.split("\n"))

def create_schedule_pdf(df, year_str, output_path):
    pdf = FPDF(orientation="P", unit="mm", format="A4") # Portrait
    pdf.set_auto_page_break(auto=True, margin=5)
    pdf.set_margins(10, 5, 10)
    pdf.add_page()
    
    font_path = "Heebo-Regular.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("Hebrew font not found.")
    
    pdf.add_font("NotoHebrew", "", font_path)
    pdf.set_font("NotoHebrew", size=14)
    
    title = f"לוח סבב הרב ביגל שבתות ל{year_str}"
    pdf.cell(0, 8, text=bidi_text(title), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(2)
    
    pdf.set_font("NotoHebrew", size=8.5)
    
    pdf_cols = ["פרשה/מועד", "תאריך", "ליל שבת", "שבת שחרית", "סעודה שלישית", "הערות"]
    # 35 + 30 + 25 + 25 + 25 + 50 = 190
    
    with pdf.table(
        borders_layout="ALL",
        cell_fill_color=(250, 249, 246),
        cell_fill_mode="ROWS",
        col_widths=(35, 30, 25, 25, 25, 50),
        text_align="CENTER",
        headings_style=FontFace(color=(0, 0, 0), fill_color=(230, 230, 230), emphasis=""),
        line_height=4.2,
        padding=0.3
    ) as table:
        header_row = table.row()
        for col in reversed(pdf_cols):
            header_row.cell(bidi_text(col))
        
        for _, row in df.iterrows():
            data_row = table.row()
            for col in reversed(pdf_cols):
                if col == "תאריך":
                    # תאריך משולב בשורה אחת כדי לחסוך גובה (למשל: א' תשרי (01/10))
                    heb = row['תאריך עברי']
                    greg = str(row['תאריך לועזי'])
                    if len(greg) >= 5:
                        greg = greg[:5] # רק יום וחודש
                    val = f"{heb} ({greg})"
                else:
                    val = str(row[col]) if pd.notna(row[col]) else ""
                
                data_row.cell(bidi_text(val))
                
    pdf.output(output_path)
    return output_path
